import tensorflow as tf 
from tensorflow import keras 
from tensorflow.keras import layers 

# Multi-Atrous Branch
class MultiAtrous(keras.Model):
    def __init__(self, dilation_rates=[6, 12, 18], upsampling=1, 
                 kernel_size=3, padding="same",  **kwargs):
        super(MultiAtrous, self).__init__(name='MultiAtrous', **kwargs)
        self.dilation_rates = dilation_rates
        self.kernel_size = kernel_size 
        self.upsampling = upsampling
        self.padding = padding

        self.dilation_convs0 = layers.Conv2D(
                                    filters       = 512, 
                                    kernel_size   = 3,  
                                    padding       = self.padding, 
                                    #dilation_rate = 6
                                )
        self.dilation_convs1 = layers.Conv2D(
                                    filters       = 512, 
                                    kernel_size   = 6,  
                                    padding       = self.padding, 
                                    #dilation_rate = 12
                                )
        self.dilation_convs2 = layers.Conv2D(
                                    filters       = 512, 
                                    kernel_size   = 9,  
                                    padding       = self.padding, 
                                    #dilation_rate = 18
                                )
        self.conv1 = layers.Conv2D(
            filters=512,
            kernel_size=1,
            padding='same')
        # Global Average Pooling Branch 
        self.gap_branch = keras.Sequential(
            [
                layers.GlobalAveragePooling2D(keepdims=True),
                layers.Conv2D(512, kernel_size=1),
                layers.Activation('relu'),
                #layers.UpSampling2D(size=self.upsampling, interpolation="bilinear")
            ] , name='gap_branch'
        )
        
    def call(self, inputs, training=None, **kwargs):
        local_feature = []

        #for dilated_conv in self.dilated_convs:
        x0 = self.dilation_convs0(inputs) 
        #x = self.gap_branch(x)
        x1 = self.dilation_convs1(inputs)
        x2 = self.dilation_convs2(inputs)
        x = tf.concat([x0,x1,x2],axis=-1)
        x = self.conv1(x)
        x = tf.nn.relu(x)
            
        return x

    def get_config(self):
        config = {
            'dilation_rates': self.dilation_rates,
            'kernel_size'   : self.kernel_size,
            'padding'       : self.padding,
            'upsampling'    : self.upsampling
        }
        base_config = super(MultiAtrous, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))
    
    
# DOLG: Local-Branch
class DOLGLocalBranch(keras.Model):
    def __init__(self, IMG_SIZE, **kwargs):
        super(DOLGLocalBranch, self).__init__(name='LocalBranch', **kwargs)
        self.multi_atrous = MultiAtrous(padding='same', upsampling=int(IMG_SIZE/32))
        self.conv1 = layers.Conv2D(1024, kernel_size=1)
        self.conv2 = layers.Conv2D(1024, kernel_size=1, use_bias=False)
        self.conv3 = layers.Conv2D(1024, kernel_size=1)
        self.bn = layers.BatchNormalization()
        self.glpool = layers.GlobalAveragePooling2D(keepdims=True)
    def call(self, inputs, training=None, **kwargs):
        # Local Branach + Normalization / Conv-Bn Module 
        local_feat = self.multi_atrous(inputs)
        local_feat = self.conv1(local_feat)
        local_feat = tf.nn.relu(local_feat)
        
        # Self-Attention
        local_feat = self.conv2(local_feat)
        local_feat = self.bn(local_feat)
        local_feat = self.glpool(local_feat)
        # l-2 norms
        norm_local_feat = tf.math.l2_normalize(local_feat, axis=-1)

        # softplus activations
        attn_map = tf.nn.relu(local_feat)
        attn_map = self.conv3(attn_map)
        attn_map = keras.activations.softplus(attn_map) 

        # Output of the Local-Branch 
        return  norm_local_feat * attn_map
