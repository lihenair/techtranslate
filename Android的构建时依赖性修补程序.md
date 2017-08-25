# Android的构建时依赖性修补程序

原文链接:[https://vincent.bernat.im/en/blog/2016-android-build-time-patch](https://vincent.bernat.im/en/blog/2016-android-build-time-patch)

这篇文章展示了如何使用[Gradle](https://gradle.org/)在*构建时修补Android*项目的*外部依赖*关系。 这充分利用了[Transform API](http://tools.android.com/tech-docs/new-build-system/transform-api)和[Javassist](http://jboss-javassist.github.io/javassist)，一个Java字节码操作工具。

```java
buildscript {
    dependencies {
        classpath 'com.android.tools.build:gradle:2.2.+'
        classpath 'com.android.tools.build:transform-api:1.5.+'
        classpath 'org.javassist:javassist:3.21.+'
        classpath 'commons-io:commons-io:2.4'
    }
}
```

*免责声明*：我不是一个经验丰富的Android程序员，所以拿这个当例子。

### 背景
本节为示例添加了一些上下文。 可以跳过它。

[Dashkiosk](https://dashkiosk.readthedocs.io/en/latest/)是适配了多显示器的管理仪表板应用程序。 它提供了一个Android应用程序，您可以在其中一个[便宜的Android手机](https://dashkiosk.readthedocs.io/en/latest/android.html#supported-devices)上安装。 在表格下，该应用程序是由Crosswalk Project Web运行时支持的嵌入式*Webview*，它提供最新的网页引擎，即使对于较旧版本的Android[^1]也是如此。

最近，在无效证书的处理方式中发现了一个[安全漏洞](https://wwws.nightwatchcybersecurity.com/2016/07/29/advisory-intel-crosswalk-ssl-prompt-issue/)。当证书无法验证时，webview将通过调用[`onReceivedSslError()`](https://crosswalk-project.org/apis/embeddingapidocs_v7/org/xwalk/core/XWalkResourceClient.html#onReceivedSslError-org.xwalk.core.XWalkView-android.webkit.ValueCallback-android.net.http.SslError-)方法来延迟决定到主机应用程序。

> *通知主机应用程序加载资源时发生SSL错误。 主机应用程序必须调用`callback.onReceiveValue(true)`或`callback.onReceiveValue(false)`。 请注意，该决定可能会被保留以备未来的SSL错误。 默认行为是弹出一个对话框。*

具体到*Crosswalk* webview的默认行为是：Android内置的只是取消加载。 不幸的是，[Crosswalk应用的修复程序](https://github.com/crosswalk-project/crosswalk/pull/3777)是不同的，作为副作用，onReceivedSslError（）方法不再被调用[^2]。

Dashkiosk提供了一个忽略TLS错误的选项[^3]。所提到的安全修复程序会中断此功能。以下示例将演示如何*修补Crosswalk以恢复以前的行为*[^4]。

### 简单方法替换
我们用这个版本的`org.xwalk.core.internal.SslUtil`类替换[`shouldDenyRequest()`](https://github.com/crosswalk-project/crosswalk/blob/crosswalk-19/runtime/android/core_internal/src/org/xwalk/core/internal/SslUtil.java#L53-L78)方法：

```java
// In SslUtil class
public static boolean shouldDenyRequest(int error) {
    return false;
}
```

#### Transform注册
*Gradle* [Transform API](http://tools.android.com/tech-docs/new-build-system/transform-api)可以在类文件转换为DEX文件之前进行操作。为了声明一个变化并注册它，在`build.gradle`中包含如下代码：

```groovy
import com.android.build.api.transform.Context
import com.android.build.api.transform.QualifiedContent
import com.android.build.api.transform.Transform
import com.android.build.api.transform.TransformException
import com.android.build.api.transform.TransformInput
import com.android.build.api.transform.TransformOutputProvider
import org.gradle.api.logging.Logger

class PatchXWalkTransform extends Transform {
    Logger logger = null;

    public PatchXWalkTransform(Logger logger) {
        this.logger = logger
    }

    @Override
    String getName() {
        return "PatchXWalk"
    }

    @Override
    Set<QualifiedContent.ContentType> getInputTypes() {
        return Collections.singleton(QualifiedContent.DefaultContentType.CLASSES)
    }

    @Override
    Set<QualifiedContent.Scope> getScopes() {
        return Collections.singleton(QualifiedContent.Scope.EXTERNAL_LIBRARIES)
    }

    @Override
    boolean isIncremental() {
        return true
    }

    @Override
    void transform(Context context,
                   Collection<TransformInput> inputs,
                   Collection<TransformInput> referencedInputs,
                   TransformOutputProvider outputProvider,
                   boolean isIncremental) throws IOException, TransformException, InterruptedException {
        // We should do something here
    }
}

// Register the transform
android.registerTransform(new PatchXWalkTransform(logger))
```

`getinputTypes()`方法应当返回变换使用的数据类型集合。本例中，我们希望转换类。另一个可能是转换资源。
`getScoes()`方法返回变换的[范围](http://google.github.io/android-gradle-dsl/javadoc/2.2/com/android/build/api/transform/QualifiedContent.Scope.html#enum.constant.detail)集合。本例中，我们只关注外部库。它也可以变换我们的类。
`inIncremental()`方法返回true，因为我们支持增量编译。
`transform()`方法期望获得所有提供的输入并拷贝它们到输出指定的位置。我们还未实现这个方法。这将导致从应用程序总删除所有外部依赖关系。

#### Noop变换
为了保持所有外部依赖，我们必须拷贝它们：

```groovy
@Override
void transform(Context context,
               Collection<TransformInput> inputs,
               Collection<TransformInput> referencedInputs,
               TransformOutputProvider outputProvider,
               boolean isIncremental) throws IOException, TransformException, InterruptedException {
    inputs.each {
        it.jarInputs.each {
            def jarName = it.name
            def src = it.getFile()
            def dest = outputProvider.getContentLocation(jarName, 
                                                         it.contentTypes, it.scopes,
                                                         Format.JAR);
            def status = it.getStatus()
            if (status == Status.REMOVED) { // ❶
                logger.info("Remove ${src}")
                FileUtils.delete(dest)
            } else if (!isIncremental || status != Status.NOTCHANGED) { // ❷
                logger.info("Copy ${src}")
                FileUtils.copyFile(src, dest)
            }
        }
    }
}
```
我们还需要两个额外的引用：

```groovy
import com.android.build.api.transform.Status
import org.apache.commons.io.FileUtils
```
由于我们处理了外部依赖关系，我们只需要管理JAR文件。因此，我们只对`jarInputs`，而不是`directoryInputs`进行迭代。处理增量版本有两种情况：文件已被删除（❶）或已被修改（❷）。 在所有其他情况下，我们可以安全地假定文件已经正确复制。

#### JAR补丁
当外部依赖时*Crosswalk*的JAR文件时，我们还需要修改它。这事代码的第一部分(替换❷)：

```groovy
if ("${src}" ==~ ".*/org.xwalk/xwalk_core.*/classes.jar") {
    def pool = new ClassPool()
    pool.insertClassPath("${src}")
    def ctc = pool.get('org.xwalk.core.internal.SslUtil') // ❸

    def ctm = ctc.getDeclaredMethod('shouldDenyRequest')
    ctc.removeMethod(ctm) // ❹

    ctc.addMethod(CtNewMethod.make("""
public static boolean shouldDenyRequest(int error) {
    return false;
}
""", ctc)) // ❺

    def sslUtilBytecode = ctc.toBytecode() // ❻

    // Write back the JAR file
    // …
} else {
    logger.info("Copy ${src}")
    FileUtils.copyFile(src, dest)
}
```
需要额外的引入来使用*Javassist*：

```groovy
import javassist.ClassPath
import javassist.ClassPool
import javassist.CtNewMethod
```
一旦找到了需要处理的JAR文件，我们添加它到类路径中，并在(❸)中检索我们感兴趣的类文件。我们找到合适的方法并删除它(❹)。接着，我们使用相同的名字(❺)添加了自定义方法。所以的操作在内存中完成。我们在❻中查看修改类的二进制文件。

剩下的步骤是重编JAR文件：

```groovy
def input = new JarFile(src)
def output = new JarOutputStream(new FileOutputStream(dest))

// ❼
input.entries().each {
    if (!it.getName().equals("org/xwalk/core/internal/SslUtil.class")) {
        def s = input.getInputStream(it)
        output.putNextEntry(new JarEntry(it.getName()))
        IOUtils.copy(s, output)
        s.close()
    }
}

// ❽
output.putNextEntry(new JarEntry("org/xwalk/core/internal/SslUtil.class"))
output.write(sslUtilBytecode)

output.close()
```
额外的引入：

```groovy
import java.util.jar.JarEntry
import java.util.jar.JarFile
import java.util.jar.JarOutputStream
import org.apache.commons.io.IOUtils
```
这里有两步。❼中，所有的类拷贝到新的JAR，除了`SslUtil`类。在❽中，添加`SslUtil`的修改二进制到JAR文件。

就这样！可以在[GitHub](https://github.com/vincentbernat/dashkiosk-android/blob/eaa36bf540f2e436e9ac9f7d257083470b7dd831/build.gradle#L93)上查看完整示例。

### 更复杂的方法替换
以上例子，新方法没有使用任何外部依赖。让我们假定在相同的类中替换`SSLErrorFormNetErrorCode()`方法：

```groovy
import org.chromium.net.NetError;
import android.net.http.SslCertificate;
import android.net.http.SslError;

// In SslUtil class
public static SslError sslErrorFromNetErrorCode(int error,
                                                SslCertificate cert,
                                                String url) {
    switch(error) {
        case NetError.ERR_CERT_COMMON_NAME_INVALID:
            return new SslError(SslError.SSL_IDMISMATCH, cert, url);
        case NetError.ERR_CERT_DATE_INVALID:
            return new SslError(SslError.SSL_DATE_INVALID, cert, url);
        case NetError.ERR_CERT_AUTHORITY_INVALID:
            return new SslError(SslError.SSL_UNTRUSTED, cert, url);
        default:
            break;
    }
    return new SslError(SslError.SSL_INVALID, cert, url);
}
```

与上一个例子的主要区别在于我们需要导入一些额外的类。

#### Android SDK引入
来自Android SDK的类不是外部依赖项的一部分。 需要单独导入。 JAR文件的完整路径是：

```groovy
androidJar = "${android.getSdkDirectory().getAbsolutePath()}/platforms/" +
             "${android.getCompileSdkVersion()}/android.jar"
```
需要在将新方法添加到SslUtil类之前加载它：

```groovy
def pool = new ClassPool()
pool.insertClassPath(androidJar)
pool.insertClassPath("${src}")
def ctc = pool.get('org.xwalk.core.internal.SslUtil')
def ctm = ctc.getDeclaredMethod('sslErrorFromNetErrorCode')
ctc.removeMethod(ctm)
pool.importPackage('android.net.http.SslCertificate');
pool.importPackage('android.net.http.SslError');
// …
```

#### 外部依赖引入
我们还必须导入`org.chromium.net.NetError`，因此，我们需要将相应的JAR放在我们的类路径中。最简单的方法是遍历所有的外部依赖关系，并将它们添加到类路径中。

```groovy
def pool = new ClassPool()
pool.insertClassPath(androidJar)
inputs.each {
    it.jarInputs.each {
        def jarName = it.name
        def src = it.getFile()
        def status = it.getStatus()
        if (status != Status.REMOVED) {
            pool.insertClassPath("${src}")
        }
    }
}
def ctc = pool.get('org.xwalk.core.internal.SslUtil')
def ctm = ctc.getDeclaredMethod('sslErrorFromNetErrorCode')
ctc.removeMethod(ctm)
pool.importPackage('android.net.http.SslCertificate');
pool.importPackage('android.net.http.SslError');
pool.importPackage('org.chromium.net.NetError');
ctc.addMethod(CtNewMethod.make("…"))
// Then, rebuild the JAR...
```
快乐黑客！

[^1]: Android4.4之前，webview已经相当过时了。从Android5开始，webview作为*单独组件*发布，并附带更新。嵌入式*Crosswalk*仍是方便的，因为你明确知道依赖那个版本。
[^2]: 我希望在之后的版本解决。
[^3]: 这似乎是有害的，你是对的。 但是，如果您有内部CA，则目前无法向Webview提供自己的信任存储。 此外，也不使用系统信任存储。 您也可能希望只带客户端证书来使用TLS进行身份验证，*Dashkiosk*支持此功能。
[^4]: *Crosswalk*是一个开源项目，另一种替代方法是修补*Crosswalk*源代码并重新编译它。 然而*Crosswalk*嵌入了*Chromium*，并且重新编译整个内容需要耗费大量资源。