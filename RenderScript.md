# RenderScript

[https://developer.android.com/guide/topics/renderscript/index.html](https://developer.android.com/guide/topics/renderscript/index.html)

RenderScript是一个在Android上为高性能运行计算密集型任务的框架。RenderScript主要面向数据并行计算，虽然串行工作负载也可以获益。RenderScript运行时并行工作可在设备上跨处理器(例如多核CPU和GPU)。

开始RenderScript前，需要理解两个主要概念：

* *语言*本身源自C99，用于编写高性能计算代码。[编写RenderScript内核](https://developer.android.com/guide/topics/renderscript/compute.html#writing-an-rs-kernel)描述如何使用它编写计算性内核。
* *控制API*用于管理RenderScript资源的生命周期和控制内核执行。它可在三种不同语言中运行：Java，Android NDK中的C++，C99派生的内核语言。

### 编写RenderScript内核
RenderScript内核通常驻留在.rs文件在**\<project_root>/src/**目录；每个.rs文件称为一个*脚本*。每个脚本包含它自己的一组内核，函数和变量。一个脚本可以包含：

* pragma声明(**#pragma version(1)**)，声明当前脚本的RenderScript内核语言版本。当前，1是唯一的有效值。
* pragma声明(**#pragma rs java_package_name(com.example.app)**)，声明从这个脚本繁盛的Java类的包名。注意你的.rs文件必须是应用包的一部分，并且不在library工程中。
* 0或者多个***可调用函数***。一个可调用函数式一个单线程RenderScript功能，可从JavaWriter代码中使用任意参数调用。这些通常用于在较大的处理管线内的初始设置活串行计算。
* 0活着多个***脚本全局***。脚本全局相当于C中的全局变量。可以从Java代码访问脚本全局变量。这些变量通常用于将参数传递给RenderScript内核。
* 0或多个***计算内核***。计算内核代表一个函数或函数集合，可指示RenderScript运行时在数据集合中并行执行。有两种计算内核：映射内核(也成为foreach内核)和简化内核。