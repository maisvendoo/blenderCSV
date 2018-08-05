# Blender plugin for Import|Export OpenBVE *.csv objects

## 1. Installation guide

* Donwload last release of plugin from [Releases section](https://github.com/maisvendoo/blenderCSV/releases)
* Open Blender, go from main menu by path File -> User Preferences -> Add-ons
* Select "Install add-on from file"

![](https://habrastorage.org/webt/kc/y4/dv/kcy4dvv4t-prv5ax-hy_lxahehk.png)

* Choose plugin zip-archive in your filesystem

![](https://habrastorage.org/webt/rf/wj/lr/rfwjlruesl3vqjtrovo7tpnzlcg.png)

* Select checkbox for addon activation

![](https://habrastorage.org/webt/zp/le/pb/zplepbd5-2yii9zd7mzqsszmqow.png)

* Press "Save user setting" for apply changes to next start of Blender

## 2. Using plugin

### 2.1. Import *.csv to blender

Now, you can import any csv model into Blender workspace. Go to menu File -> Import -> OpenBVE *.csv model

![](https://habrastorage.org/webt/oz/wl/wo/ozwlwoh7nv55fjng8zjg6imq08q.png)

and open your model from filesystem.

![](https://habrastorage.org/webt/lj/ok/vh/ljokvh3odnpolo2z7mcqbfmyxo8.png)

In import settings, you can choose option for model transformation from OpenBVE left hand coordinate system to Blender right hand coordinate system

![](https://habrastorage.org/webt/kw/9g/qn/kw9gqnkbrcd9hpkk6s-asdvre1a.png)

This setting enable by default, but you can disabled it

![](https://habrastorage.org/webt/js/y6/qu/jsy6qumzoanb66n0hq_6e0zifee.png)

**Attation!** CSV commands **Shear** and **ShearAll** do not supported in current version. It will fixed in future version of plugin

### 2.2. Export from Blender to *.csv

1. Select your model in Blender and switch to **Object Mode**

![](https://habrastorage.org/webt/n1/ok/dp/n1okdpwjr9d6i5r0e8x_ux_hggk.png)

2. Select menu item File -> Export -> OpenBVE *.csv model
3. Choose export options

![](https://habrastorage.org/webt/lf/x_/1h/lfx_1hv9cbinoy2xzid0d_ycziy.png)

* Transform coordinate system - conversion to OpenBVE left hand coordinates. It option enabled by default
* Use Face2 command - all face generation commands will be present in CSV as AddFace2
* Use decale transparent color - set components for decale color

**Attantion!** In current version decale color applied to all meshes in model

* Copy textures in separated folder - all textures will copired to separated folder, which will created near CSV file and will has name *model file name-textures*

* Press button "OpenBVE model (*.csv)" to export
* Check result in OpenBVE ObjectViewer

![](https://habrastorage.org/webt/-v/no/ix/-vnoixjsdb-jnyzgve0usawv0he.png)

Enjoy!










