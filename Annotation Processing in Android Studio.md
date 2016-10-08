# Annotation Processing in Android Studio

原文链接：[https://medium.com/@aitorvs/annotation-processing-in-android-studio-7042ccb83024#.bt3os8v2n](https://medium.com/@aitorvs/annotation-processing-in-android-studio-7042ccb83024#.bt3os8v2n)

自动代码生成是非常强力的工具，每个软件工程师都应当使用它。它避免了没人愿意编写的繁琐和重复的模板代码，主要是因为它们通常是无趣和高度易错的。

对于Java开发者，这里有一些工具来缓解代码生成的痛苦。从像[JavaPoet](https://github.com/square/javapoet)到使用基于模板的解决方案[Apache Velocity](http://velocity.apache.org/engine/1.7/vtl-reference.html),它们都为实现我们的目标铺平了道路。

我不会讨论任何伟大的工具和如何使用它们。本文我将关注如何**使用和处理注解**来触发Android Studio中的代码生成。

### 注解
我相信你们都有意无意的使用了注解。注解是类的**元数据**，可以与类，方法，域，参数甚至其他注解关联。可以在运行时——使用反射——和/或者在编译时使用注解处理器来访问它们。查看以下代码。

```
public class Foo {
    private Date mDate;
    public Foo(@NonNull Date date){...};
    ...
}
```
你们以前肯定看过这种代码。现在，你们都知道使用*null*参数调用*Foo*的构造器，Android Studio会抱怨。好吧，你猜对了，Android Studio是处理*@NonNull*注解来确定的。

我们将做相同的事。我们将创建自定义注解及其相关处理器。在编译时，每当遇到使用自定义注解标注的特定类，该处理器都将自动生成代码。

### ‘处理’和注解处理器
在讨论注解生成器之前，让我们大概了解下当Android Studio编译我们的Java应用时发生了什么。
当构建我们的应用，Android Studio(除了许多其他事)将在所有处理器模块(纯Java代码)之前构建。之后，它将开始处理Android工程中所有注解——包括我们自定义的注解。
每个处理器怎样处理它感兴趣的注解，完全取决于处理器自己。
让我们开发一个库来简化[打包](https://developer.android.com/reference/android/os/Parcel.html)对象的任务——是的，我也反感样板代码。
这个库与其他库一样工作，注解你想打包的类，库将自动生成所有样板代码。我们所要做的是一个自定义注解和相应的注解处理器——所有魔法来遍历类字段，生成[Parcelable](https://developer.android.com/reference/android/os/Parcelable.html)接口方法，*yadda yadda yadda*，我将明智的忽略这里:D

### 例子(骨干)代码
例子由一个简单的app，一个包含自定义注解的库和注解处理器(aka 编译器)构成。基本的包名将命名为，例如，com.example,autoparcel。

#### 自定义注解
创建一个名为***library***的**Java模块**，这里，创建你自己的注解。
注解名为*AutoParcel*——它将获取POJO并使它们实现*Parcelable*接口，我很擅长命名的事情。

![](https://cdn-images-1.medium.com/max/1600/1*iifNMf2dG6pLEWZqP5hSLw.png)

```
package com.example.autoparcel;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;
@Target(ElementType.TYPE) // on class level
@Retention(RetentionPolicy.SOURCE) // not needed at runtime
public @interface AutoParcel {}
```
注意我们还可以注解自定义注解(1)通知框架我们的注解只能用于类；(2)我们的注解处理器处理后，注解将被编译器丢弃。

让我们看一下*library/buikd.gradle*文件。我们需要添加*source*和*target*来兼容Java1.7。因为注解(库)将用在Android工程中。

```
apply plugin: 'java'

// This module will be used in Android projects, need to be
// compatible with Java 1.7
sourceCompatibility = JavaVersion.VERSION_1_7
targetCompatibility = JavaVersion.VERSION_1_7

dependencies {
    ...
}
```

### 注解处理器
现在是有趣的部分，注解处理器。
创建名为例如*编译器*的**Java模块**。注意我们不需要这个模块是一个Android模块，因为它不是任何Android应用的一部分。它只是Java文档，由编译器调用来处理我们的自定义注解。我们甚至可以使用高于1.7的Java版本来编写我们的处理器。
现在创建处理器类，名为*AutoParcelProcessor*，并放置于包名例如，*com.example.autoparcel.codegen*中。

![](https://cdn-images-1.medium.com/max/1600/1*ae1bIzz7l_PknqupuQU11g.png)

```
package com.example.autoparcel.codegen;
@SupportedAnnotationTypes("com.example.autoparcel.AutoParcel")
public final class AutoParcelProcessor extends AbstractProcessor {
  @Override
  public boolean process(
           Set<? extends TypeElement> annotations, 
           RoundEnvironment env) {
    ...
  }
}
```
这里有些事需要注意。

1. 处理器应当扩展自***AbstractProcessor**类。
2. 需要添加自定义注解的全路径
3. 需要实现***process()***方法。构件时调用该方法来处理之前创建的*@AutoParcel*注解，这里我们实现了所以的魔法。

> 提示：如果想在Android Studio中获取指定文件的全路径，只需要右键它并选择Copy Reference。

![](https://cdn-images-1.medium.com/max/1600/1*u41wF8vgFMXetitjt98zzA.png)

我不会在这里实现完整的处理器。只打算将它分解为简单的方法调用来处理所有注释了*@AutoParcel*的类型，并生成一些Java文件。

当再没有任何指定类型的注解需要处理时，*process()*方法将返回*true*。

```
package com.example.autoparcel.codegen;
...
@Override
public boolean process(
      Set<? extends TypeElement> annotations, 
      RoundEnvironment env) {
    
    Collection<? extends Element> annotatedElements =
            env.getElementsAnnotatedWith(AutoParcel.class);
    List<TypeElement> types = 
          new ImmutableList.Builder<TypeElement>()
            .addAll(ElementFilter.typesIn(annotatedElements))
            .build();

    for (TypeElement type : types) {
        processType(type);
    }

    // We are the only ones handling AutoParcel annotations
    return true;
}
private void processType(TypeElement type) {
    String className = generatedSubclassName(type);
    String source = generateClass(type, className);
    writeSourceFile(className, source, type);
}
private void writeSourceFile(
        String className, 
        String text, 
        TypeElement originatingType) {
    try {
        JavaFileObject sourceFile =
            processingEnv.getFiler().
                createSourceFile(className, originatingType);
        Writer writer = sourceFile.openWriter();
        try {
            writer.write(text);
        } finally {
            writer.close();
        }
    } catch (IOException e) {// silent}
}
...
```
最后，我们已经实现了处理器，需要告诉框架来使用它。创建一个***javax处理器文件***。框架编译器查找它来处理所有注解。在Android Studio中，方法如下：

1. 创建一个资源文件夹，<i>compiler/src/main/<b>resources</b></i>
2. 资源文件夹下，创建META_INF目录，<i>compiler/src/main/resources/<b>META_INF</b></i>
3. 在*META_INF*中创建***services***目录，<i>compiler/src/main/resources/META_INF/<b>services</b></i>
4. 在*services*目录中创建名为**javax.annotation.processing.Processor**的文件

![](https://cdn-images-1.medium.com/max/1600/1*B__ZfWsGptw3M0cQ7tm7Ng.png)

文件需要包含每个创建的处理器的全路径。

```
com.example.autoparcel.codegen.AutoParcelProcessor
```

都在这里了。你创建了你的第一个注解和注解处理器。

### 使用
你得到了这个魔法，现在你有一个自定义注解和它的处理器来将无聊的POJO变成评论的Parcelable对象，让我们使用它。
在你的*settings.gradle*文件中，只需要添加这些模块。

```
include ':app', ':compiler', ':library'
```

在你的*app/build.gradle*只需要添加*library*模块——包含自定义注解——和*compiler*注解处理器模块。

```
...
dependencies {
    ...
    provided project(':library')
    apt project(':compiler')
    ...
}
```
注意我添加*library*依赖使用*provided*，而不是*compile*。因为我们的注解将在编译时处理，我们不需要将它包含在最终的应用代码。

最后，在应用里使用它。在你的POJO对象前添加注解，并让处理器做余下的工作。

```
@AutoParcel
public class Foo{
...
}
```

> 我推荐使用[android-apt](https://bitbucket.org/hvisser/android-apt)插件来允许Android Studio与注解处理器一起工作。

### 真正(完整)的实现
如果你到了这里，现在你应该能够在Android Studio中做注解处理了。
文中使用的例子是一个真正的库，只需为对象增加注解，就可让他们具有[Parcelale](https://developer.android.com/reference/android/os/Parcelable.html)性。你可以在[这里](https://github.com/aitorvs/auto-parcel)检出库。