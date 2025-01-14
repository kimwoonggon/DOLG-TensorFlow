
![3-Figure2-1](https://user-images.githubusercontent.com/17668390/150056333-bb5af4fa-33f4-42df-9dc7-fbebbcbef862.png) ![4-Figure3-1](https://user-images.githubusercontent.com/17668390/150056354-6f23afae-4c01-434a-b3e9-96099b61924e.png)

# DOLG-TensorFlow

This is an unofficial implementation of **Deep Orthogonal Fusion of Local and Global Features (DOLG)** in `TensorFlow 2 (Keras)`. [Paper](https://arxiv.org/pdf/2108.02927.pdf). 

It seeks to design an effective single-stage solution by integrating local and global information inside images into compact image representations. It attentively extracts representative local information with multi-atrous convolutions and self-attention at first. Components orthogonal to the global image representation are then extracted from the local information. At last, the orthogonal components are concatenated with the global representation as a complementary, and then aggregation is performed to generate the final representation.

**Prerequisites**: Check [requirements.txt](https://github.com/innat/DOLG-TensorFlow/blob/main/requirements.txt)

## Install 

```bash 
pip install dolg-tensorflow

or
git clone https://github.com/innat/DOLG-TensorFlow.git
```

## Usage

**First**, create a model with two output branch, one for **local branch** and other for **global branch**. It's needed for DOLG model. See the demo below.

```python
base = applications.EfficientNetB0(...)
new_base = keras.Model(
    [base.inputs], 
    [
        base.get_layer('block5c_add').output,       # fol local branch 
        base.get_layer('block7a_project_bn').output # for global branch 
    ]
)
```

**second**, now use the above created model as follows.

```python
from models.DOLG import DOLGNet

dolg_net = DOLGNet(new_base, num_classes=num_classe, activation='softmax')
dolg_net.build_graph().summary()
```

Apart from the above approach, we can also integrate dolg layers with our custom model. Here is one example, 

```python
# component of DOLG model
from layers.GeM import GeneralizedMeanPooling2D
from layers.LocalBranch import DOLGLocalBranch
from layers.OrtholFusion import OrthogonalFusion

vision_input = keras.Input(shape=(img_shape, img_shape, 1), name="img")
x = Conv2D(...)(vision_input)
x = Conv2D ...
y = x = DOLGLocalBranch(IMG_SIZE=img_shape)(x)

x = MaxPooling2D(...)(x)
x = Conv2D ...
gem_pool = GeneralizedMeanPooling2D()(x)
gem_dens = Dense(1024, activation=None)(gem_pool)

vision_output = OrthogonalFusion()([y, gem_dens])
vision = keras.Model(vision_input, vision_output, name="vision")
vision.summary(expand_nested=True, line_length=110)
```

## Code Examples

The **DOLG** concept can be integrated into any computer vision models i.e. `NFNet`, `ResNeSt`, or `EfficietNet`. Here are some end-to-end code examples.

- [DenseNet DOLGNet Malaria](https://github.com/innat/DOLG-TensorFlow/blob/main/code_examples/DenseNet_DOLGNet_Malaria.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1VI7qZQZX_sWZZM8eKN98gCbiY3Ju1NpY?usp=sharing)
- [EfficientNet DOLGNet Oxford Flowers 102](https://github.com/innat/DOLG-TensorFlow/blob/main/code_examples/EfficientNet_DOLGNet_Oxford_Flowers_102.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1WvxR6gh0SzqcYUnSNnVQRw9UiFzgFMgm?usp=sharing)
- [ResNet DOLGNet Cmaterdb](https://github.com/innat/DOLG-TensorFlow/blob/main/code_examples/ResNet_DOLGNet_Cmaterdb.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1uEV9GsEZnTyWoilVww8d_Jmn3cAcefZr?usp=sharing)


## References and Other Implementation 
- [Blogs](https://mp.weixin.qq.com/s/7B3hZUpLtTt8NcGt0c-77w).
- [Official-Code](https://github.com/feymanpriv/DOLG-paddle)
- [PyTorch-Code](https://github.com/dongkyuk/DOLG-pytorch).
