把玩Java注解处理

我通过Tweet发现了[Lombok项目](http://projectlombok.org/)，并且当我看到一个注解就可以在源码编译时透明的触发代码自动生成，这肯定有什么技巧。他们是怎么做到的呢？

一番探索之后，我发现了Java的注解处理API，以及如何使用SPI(Service Provider Interface)在编译时透明的调用注解处理器。这里是处理流程：

首先，我们创建一个简单的注解类型(忽略包名和引入)：

```
@Retention(RetentionPolicy.SOURCE)
public @interface PrintMe {}
```

使用@Retention注解，我们指定超过编译时间后不处理这类型的注解，所以编译器可以放弃他们。

接着，我们创建一个注解处理器，它会打印那些使用@PrintMe注解的元素。我们可以继承自AbstractProcessor类。使用@SupportedAnnotationTypes注解，指定要处理的注解：

```
@SupportedAnnotationTypes(
  {"com.programmaticallyspeaking.aptdemo.PrintMe"}
)
public class AnnotationProcessor extends AbstractProcessor {
```

要实现的主要方法是process：

```
public boolean process(Set<? extends TypeElement> annotations,
                         RoundEnvironment env) {
```

我们获取当前的Messager实例使得能够打印消息：

```
Messager messager = processingEnv.getMessager();
```

接着遍历注解(这里只有一个注解，所以代码比它需要的更通用)，以及由它们注解的元素：

```
for (TypeElement te : annotations) {
      for (Element e : env.getElementsAnnotatedWith(te)) {
```

这里，我们可以做很多有趣的是，但是现在，我们只打印每个被注解元素：

```
messager.printMessage(Diagnostic.Kind.NOTE,
                                 "Printing: " + e.toString());
```

最后，我们括起来并返回true来声明处理的注解，这样没有其他注解可以使用它们：

```
      }
    }
    return true;
  }
```

为了避免在注解处理器执行时有于代码版本的警告，我们指定处理当前执行环境支持的最新代码版本：

```
  @Override
  public SourceVersion getSupportedSourceVersion() {
    return SourceVersion.latestSupported();
  }
}
```

这就是它的注解处理器。接下来，我们需要指定注解处理器驻留在哪里来使用SPI。我们通过创建一个在META-IN/services目录里名为*javax.annotation.processing.Processor*的文件做到这点。该文件内容应当是：

```
com.programmaticallyspeaking.aptdemo.AnnotationProcessor
```

而且，Maven编译器插件需要一些配置。首先提高源和目标版本，第二禁用注解处理器(因为插件可能由于我们的SPI文件感到困惑)：

```
<plugin>
  <artifactId>maven-compiler-plugin</artifactId>
  <version>2.3.2</version>
  <configuration>
    <source>1.6</source>
    <target>1.6</target>
    <!-- Disable annotation processing for ourselves. -->
    <compilerArgument>-proc:none</compilerArgument>
  </configuration>
</plugin>
```

项目完整代码可以从这里获取[GitHub](https://github.com/provegard/aptdemo)。

构建项目会生成aptdemo-1.0-SNAPSHOT.jar文件。下面是测试代码：

```
import com.programmaticallyspeaking.aptdemo.PrintMe;

@PrintMe
public class Test {
  @PrintMe
  public static void a1(int x) {
  }

  public static void a2(String[] arr) {
  }
}
```

编译该文件，类路径带aptdemo的JAR，将得到：

```
$ javac -cp target/apt-demo-1.0-SNAPSHOT.jar Test.java
Note: Printing: Test
Note: Printing: a1(int)
```

注意，注解处理不需要编译标志。它是完全透明的。还要注意a2方法，它没有带注解，编译期不被打印。

就此打住。快乐的注解处理吧!:-)