# sovling the video issue

by default, videos in web pages can not be shown.
To show vide, we need to add the following in the args.gn

``` sh
proprietary_codecs = true
ffmpeg_branding = "Chrome"
```

# adding API for getting error message


``` sh
git apply log_message.patch
```

# build llvm ir


1. apply `wllvm-build.patch`, 


``` sh
git apply wllvm-build.patch
```

2. Create a build directory 

``` sh
gn gen out/llvm-build
```


3. update out/llvm-build/args.gn with the following content

```sh
custom_toolchain="//build/toolchain/linux:wllvm_x64"
clang_use_chrome_plugins = false
treat_warnings_as_errors = false
use_rtti = true
```

Note: we need to use enable rtti (by setting `use_rtti` to `true`)
to make the C++ type analysis work, otherwise, inheritance information 
is not available at all (phasar uses runtime type information to
derive type hierarchy).


4. create a python virtualenv and install wllvm

``` sh
python3 -m venv venv
source venv/bin/activate

pip install wllvm
```

5. build webgl related source with clang


```sh
export PATH=<chromium_root>/src/third_party/llvm-build/Release+Asserts/bin:$PATH
export LLVM_COMPILER=clang # specify the version of clang here
autoninja -C out/testing third_party/blink/renderer/modules/webgl 
```

5. extracting IR code

``` sh

cd <build_dir>/obj/third_party/blink/renderer/modules/webgl/webgl

for f in `ls *.o`;do
    extract-bc $f
done

# link all the IR code together

llvm-link-10 *.bc -o webgl_all_rendering_code.bc
```

# android config

args.gn:


``` sh
target_os = "android"
target_cpu = "arm64"
# is_gpu_asan = true
enable_nacl = false
# is_official_build=true

proprietary_codecs = true
ffmpeg_branding = "Chrome"
```

# building commands

for desktop chrome builds:

for desktop chrome:

``` sh
autoninja -C out/<outdir> chrome
```

building only blink webgl parts:

``` sh
autoninja -C out/<outdir> third_party/blink/renderer/modules/webgl:webgl
```


for android chrome:

``` sh
autoninja -C out/<outdir> chrome_public_apk
```
