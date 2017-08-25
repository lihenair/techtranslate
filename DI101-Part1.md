# DI101 - 第一部分
## Android平台依赖注入

当我们第一次研究软件工程时，通常会碰到：

<center><font color=gray size=5>*软件应当SOLID。*</font></center>

但是实际上这意味着什么？好吧，让我没说，**首字母缩写的每个字符意味着对架构真正重要的东西**，例如：

* [单一职责原理](https://en.wikipedia.org/wiki/Single_responsibility_principle)
* [开闭原理](https://en.wikipedia.org/wiki/Open/closed_principle)
* [李氏替换原理](https://en.wikipedia.org/wiki/Liskov_substitution_principle)
* [接口隔离原理](https://en.wikipedia.org/wiki/Interface_segregation_principle)
* [依赖反转原理](https://en.wikipedia.org/wiki/Dependency_inversion_principle)是依赖注入所基于的核心概念。

简单地说，需要提供一个包含所有需要对象的类来执行它的职责。

### 概述
依赖注入听起来想一个非常复杂的属于，事实上，它非常简单，可以用这个例子解释：

```
@Scope
@Retention(RetentionPolicy.RUNTIME)
  public @interface DetailScope {
}
```

我可以看到，在第一种情况下，我们是在构造函数中创建依赖的，而在第二种情况下，它作为参数传递过来。第二种情况就是所说的依赖注入。这样做，类不依赖于以来的实现，只使用依赖。
此外，基于参数是通过构造函数还是方法传递古来，我们会分别讨论构造函数依赖注入和方法依赖注入：

```
@DetailScope
@Subcomponent
public interface DetailComponent {
  void inject(DetailActivity target);
}
```
如果想更多地了解依赖注入，一定要看[Dan Lew](https://twitter.com/danlew42)做的[令人惊讶的演讲](https://realm.io/news/daniel-lew-dependency-injection-dagger/)，这个演讲实际上启发了这个概述。

在Android上，当涉及到特定问的框架时，我没有不同的选择，但最有名的是[Dagger 2](http://google.github.io/dagger/)，首先由Square的帅哥们构造，之后由Google接手。具体来说，Dagger 1由Square实现了第一版，之后G家接手了工程，并创建了第二版，主要的改变是基于注解并在编译时实现它的注入功能。

### 导入框架
设置Dagger不是大问题，但它需要在工程的根目录的*build.gradle*文件中添加他的依赖来导入**android-apt**插件。

```groovy
buildscript{
  ...
  dependencies{
    ...
    classpath ‘com.neenbedankt.gradle.plugins:android-apt:1.8’
  }
}
```
接着，需要在app的*build.gradle*文件的顶部，Android 应用插件之下应用**android-apt**插件：

```groovy
apply plugin: ‘com.neenbedankt.android-apt’
```
这里，只需要添加依赖就可以使用库和它的注解了：

```groovy
dependencies{
    ...
    compile ‘com.google.dagger:dagger:2.6’ 
    apt ‘com.google.dagger:dagger-compiler:2.6’
    provided ‘javax.annotation:jsr250-api:1.0’
}
```
> *需要最后的依赖因为@Generated注解在Android上不可用，[它是纯Java的](https://docs.oracle.com/javase/7/docs/api/javax/annotation/Generated.html)。*

### Dagger Module
为了注入依赖，首先需要告诉框架可以提供什么(例如，Context)以及如何构建这个特定对象。为了做到这一点，我们使用**@Module**注解注释一个特定类(以便Dagger可以读取它)扫描**@Privode**注解的方法，并生成一个有向图来获取请求的对象。

让我们看一个例子，我们创建一个提供**ConnectivityManager**的模块。因此需要在模型的构造器中传递**Context**参数：

```java
@Singleton
@Component(
  modules = {
    ApplicationModule.class, ApiModule.class, 
    DatabaseModule.class, ImageApiModule.class
   }
  )
public interface ApplicationComponent {
  void inject(ApiService service);
  void inject(MainActivity activity);
  void inject(DetailActivity activity);
  DetailComponent add(DetailModule module);
}
```
> Dagger非常有趣的一个特性是通过简单地Singleton注释一个方法来处理Java继承的所有问题。

### Components
一旦有了模型，我们需要告诉Dagger我们想将依赖注入到哪里：在Compentent中，一个特别的注解接口，在这里创建不同的方法，其中的参数是依赖注入的类。

来看这个例子，我们希望**MainActivity**类可以接收**ConnectivityManager**(或依赖图中的其他依赖)。我们可以简单做如下处理：

```java
public class App extends Application{
  private ApplicationComponent component;
  private DetailComponent detailComponent;
  
  @Override
  public void onCreate() {
    super.onCreate();
    …
  }
  …
  
  public DetailComponent createDetailComponent() {
    detailComponent = component.add(new DetailModule());
    return detailComponent;
  }
  …
}
```
> *可以看到，@Component注解获得一些参数，一个是支持模型的数组，是可提供的依赖。在我们的例子中，它们可以是Context和ConnectivityManager，因为它们声明在ApplicationModule中。*

### 连接
在这一点上，我们需要做的是尽快创建Component(例如在Application类的onCreate阶段)并返回它，以便类可以用它来注入依赖：

```java
public void releaseDetailComponent() {
  detailComponent = null;
}
```
> *为了让框架自动生成DaggerApplicationComponent，我们需要构建项目，以便让Dagger可以扫描我们的代码库并生成需要的部分。*

在**MainActivity**中，尽管，需要做的两件事是对需要注入的属性添加@Inject注解和调用**ApplicationComponent**接口中声明的方法(注意，最后部分根据我们执行那种注入，但现在可以忽略它来简化)，以便我们的依赖注入，并可以随意使用它们：

```java
public class DetailActivity extends AppCompatActivity {
  @Override
  protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_device_info);
    ((App) getApplication()).createDetailComponent().inject(this);
    …
  }
  
  @Override
  protected void onDestroy() {
    super.onDestroy();
    ((App) getApplication()).releaseDetailComponent();
  }
}
```

### 结论
当然，我们可以手动执行依赖注入，管理所有不同对象，但Dagger屏蔽了模板代码关联的大量的“噪声”，提供了一些优秀的特性(例如**Singleton**)，否则Java中的处理会相当糟糕。
