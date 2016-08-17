#使用Dagger 2进行依赖注入 - API介绍

原文链接：[http://frogermcs.github.io/dependency-injection-with-dagger-2-the-api/](http://frogermcs.github.io/dependency-injection-with-dagger-2-the-api/)

本文是展示在Android应用中使用Dagger2进行依赖注入的系列文章之一。今天我想深入研究Dagger2的基础，并遍历这个依赖注入框架的所有API。

##Dagger 2
前文我提到了DI框架带给我们的好处 - 它用少量代码绑定了所有依赖关系。Dagger2是一个DI框架的例子，它生成了大量的代码模板。但是，为什么它更优秀呢？现在，它是唯一一个模拟用户手写自动生成完全可追溯源码的DI框架。这意味着依赖关系图就是魔法门。Dagger2相较其他注入框架缺少动态性(未使用反射)，但生成代码的简单性和效率与手写代码无异。

###Dagger 2基础
Dagger2 API如下：

	public @interface Component {
		Class<?>[] modules() default {};
		Class<?>[] dependencies() default {};
	}
	
	public @interface Subcomponent {
		Class<?>[] modules() default {};
	}
	
	public @interface Module {
		Class<?>[] includes() default {};
	}
	
	public @interface Provides {
	}
	
	public @interface MapKey {
		boolean unwrapValue() default true;
	}
	
	public interface Lazy<T> {
		T get();
	}

还有其他几个JSR-330(Java中的依赖注入标准)定义的注解，也用在Dagger2中：

    public @interface Inject {
    }
    
    public @interface Scope {
    }
    
    public @interface Qualifier {
    }

让我们逐个击破。

####@Inject注解

首先最重要的DI是`@Inject`注解。作为JSR-330标准的一部分，标记那些依赖注入框架提供的依赖。Dagger2中，有3种不同的方式提供依赖：

#####构造器注入

构造器使用`@Inject`：

	public class LoginActivityPresenter {
	
		private LoginActivity loginActivity;
		private UserDataStore userDataStore;
		private UserManager userManager;
		
		@Inject
		public LoginActivityPresenter(LoginActivity loginActivity,
		  UserDataStore userDataStore,
		  UserManager userManager) {
			this.loginActivity = loginActivity;
			this.userDataStore = userDataStore;
			this.userManager = userManager;
		}
	}

所有参数都从依赖图中获取。`@Inject`注解用在构造器还使得这个类成为依赖图的一部分。这意味它可以也随时注入，例如：

	public class LoginActivity extends BaseActivity {
	
	@Inject
	LoginActivityPresenter presenter;
	
	//...
	}

本例中的限制是，我们只能对类中的一个构造器使用`@Inject`注解.

#####域注入

另一个方法是对特殊域使用`@Inject`注解：

	public class SplashActivity extends AppCompatActivity {
	    
	    @Inject
	    LoginActivityPresenter presenter;
	    @Inject
	    AnalyticsManager analyticsManager;
	    
	    @Override
	    protected void onCreate(Bundle bundle) {
	        super.onCreate(bundle);
	        getAppComponent().inject(this);
	    }
	}

本例中注入过程称为“手工”，方式如下：

	public class SplashActivity extends AppCompatActivity {
	    
	    //...
	    
	    @Override 
	    protected void onCreate(Bundle bundle) {
	        super.onCreate(bundle);
	        getAppComponent().inject(this);    //Requested depenencies are injected in this moment
	    }
	}

该调用之前，我们的依赖值为null。

域注入的限制是域不能声明为`private`。为什么？简而言之，生成的代码会明确的调用它们，像这样：

	//This class is generated automatically by Dagger 2
	public final class SplashActivity_MembersInjector implements MembersInjector<SplashActivity> {
	
	    //...
	
	    @Override
	    public void injectMembers(SplashActivity splashActivity) {
	        if (splashActivity == null) {
	            throw new NullPointerException("Cannot inject members into a null reference");
	        }
	        supertypeInjector.injectMembers(splashActivity);
	        splashActivity.presenter = presenterProvider.get();
	        splashActivity.analyticsManager = analyticsManagerProvider.get();
	    }
	}

#####方法注入

最后一个使用`@Inject`提供依赖的方式是注解类中的公共方法：

	public class LoginActivityPresenter {
	    
	    private LoginActivity loginActivity;
	    
	    @Inject 
	    public LoginActivityPresenter(LoginActivity loginActivity) {
	        this.loginActivity = loginActivity;
	    }
	
	    @Inject
	    public void enableWatches(Watches watches) {
	        watches.register(this);    //Watches instance required fully constructed LoginActivityPresenter
	    }
	}

所有方法参数由依赖图提供。但是为什么我们需要方法注入呢？当我们需要传类实例自身(`this`引用)来注入到依赖时，我们需要提供函数注入。函数注入在构造器调用后立即调用，因此这意味着我们需要传递完全构造的`this`。

####@Module注解

`@Module`是Dagger2 API的一部分。这个注解用于标记提供依赖的类 - 感谢这个注解，Dagger就知道在那里需要构造对象了。

	@Module
	public class GithubApiModule {
	    
	    @Provides
	    @Singleton
	    OkHttpClient provideOkHttpClient() {
	        OkHttpClient okHttpClient = new OkHttpClient();
	        okHttpClient.setConnectTimeout(60 * 1000, TimeUnit.MILLISECONDS);
	        okHttpClient.setReadTimeout(60 * 1000, TimeUnit.MILLISECONDS);
	        return okHttpClient;
	    }
	
	    @Provides
	    @Singleton
	    RestAdapter provideRestAdapter(Application application, OkHttpClient okHttpClient) {
	        RestAdapter.Builder builder = new RestAdapter.Builder();
	        builder.setClient(new OkClient(okHttpClient))
	               .setEndpoint(application.getString(R.string.endpoint));
	        return builder.build();
	    }
	}

####@Provides注解

这个注解用在`@Module`类。`@Provides`标记Module中返回依赖的方法。

	@Module
	public class GithubApiModule {
	    
	    //...
	    
	    @Provides   //This annotation means that method below provides dependency
	    @Singleton
	    RestAdapter provideRestAdapter(Application application, OkHttpClient okHttpClient) {
	        RestAdapter.Builder builder = new RestAdapter.Builder();
	        builder.setClient(new OkClient(okHttpClient))
	               .setEndpoint(application.getString(R.string.endpoint));
	        return builder.build();
	    }
	}

####@Component注解

这个注解用于构建接口，该接口把所有封装在一起。这里，我们定义需要依赖的模块(或组件)。这里定义了那些图依赖应当公开可见(可注入)，我们的组件可以注入哪里。`@Component`是连接`@Module`和`@Inject`的桥梁。

示例代码中`@Component`使用了2个模块，可以向`GithubClientApplication`注入依赖，并使其他3个依赖公共可见：

	@Singleton
	@Component(
	    modules = {
	        AppModule.class,
	        GithubApiModule.class
	    }
	)
	public interface AppComponent {
	
	    void inject(GithubClientApplication githubClientApplication);
	
	    Application getApplication();
	
	    AnalyticsManager getAnalyticsManager();
	
	    UserManager getUserManager();
	}

而且`@Component`可以依赖其他组件，可以定义生命周期(将来某期我将写作用域)：

	@ActivityScope
	@Component(      
	    modules = SplashActivityModule.class,
	    dependencies = AppComponent.class
	)
	public interface SplashActivityComponent {
	    SplashActivity inject(SplashActivity splashActivity);
	
	    SplashActivityPresenter presenter();
	}

####@Scope注解

	@Scope
	public @interface ActivityScope {
	}

JSR-330标准的又一部分。在Dagger2中，`@Scope`用来实现自定义作用域注解。总之，它使得依赖非常类似与单例。注解的依赖是单例的，但是也与组件的声明周期有关(不是整个应用)。但是如前所述 - 我们将在下一篇里深入研究作用域。现在，值得提醒的是所有自定义作用域行为是一样的(从代码角度) - 他们保持单一对象实例。但是它们也用在图形校验过程，该过程有助于尽快捕获依赖图的结构问题。

现在是一些不重要，不常使用的注解：

####@MapKey

这个注解用于定义依赖集合(映射和集)。例子是自解释的：

**定义**

	@MapKey(unwrapValue = true)
	@interface TestKey {
	    String value();
	}

**提供依赖**

	@Provides(type = Type.MAP)
	@TestKey("foo")
	String provideFooKey() {
	    return "foo value";
	}
	
	@Provides(type = Type.MAP)
	@TestKey("bar")
	String provideBarKey() {
	    return "bar value";
	}

**使用**

	@Inject
	Map<String, String> map;
	
	map.toString() // => „{foo=foo value, bar=bar value}”

`@MapKey`注解现在只支持两种类型的键值 - String和Enum。

####@Qualifier

`@Qualifier`注解帮助我们创建依赖的"tag"，依赖有同样的接口。想想一下，你需要提供两个`RestAdapter
`对象 - 一个用于Github API，零一二用于facebook API。 `Qualifier`会帮助你识别它们：

**命名依赖**

	@Provides
	@Singleton
	@GithubRestAdapter  //Qualifier
	RestAdapter provideRestAdapter() {
	    return new RestAdapter.Builder()
	        .setEndpoint("https://api.github.com")
	        .build();
	}
	
	@Provides
	@Singleton
	@FacebookRestAdapter  //Qualifier
	RestAdapter provideRestAdapter() {
	    return new RestAdapter.Builder()
	        .setEndpoint("https://api.facebook.com")
	        .build();
	}

**注入依赖**

	@Inject
	@GithubRestAdapter
	RestAdapter githubRestAdapter;
	
	@Inject
	@FacebookRestAdapter
	RestAdapter facebookRestAdapter;

全部介绍完毕。我们已经了解了Dagger 2 API的所有重要组件。

###App实例

现在，是时候上手练练了。我们将实现简单的Github客户端应用，该应用基于Dagger2构建。

####想法

我们的Github客户端有3个页面和非经简单的用户用例。流程如下：

1. 输入Github用户名
2. 如果存在就显示所有的公开仓库列表
3. 点击列表条目，显示仓库详情

应用样子如下：
![](http://frogermcs.github.io/images/14/app_flow.png)

从DI的角度，我们的架构如下：

![](http://frogermcs.github.io/images/14/local_components.png)

总之 - 每个activity有自己的依赖图。每个图(`_Component`类)有两个对象 - `_Presenter`和`_Activity`。而且每个对象从全局组件得到依赖 - `AppComponent`，它包含其他组件`Application`， `UserManager`，`RepositoriesManager`等。

![](http://frogermcs.github.io/images/14/app_component.png)

说道`AppComponent`，只要仔细观察这个接口。他包含两个模块：`AppModule
`和`GithubApiModule`。
`GithubApiModule`提供如`OkHttpClient`和`RestAdapter`的依赖，这些依赖值用在这个模块中的其他依赖。在Dagger2中，我们可以控制哪些对象在组件外可见。在我们的例子中，我们不想暴露提到的对象。相反我们只暴露了`UserManager`和`RepositoriesManager`，因为只有这些对象用在我们的Activities中。所有这些通过返回值为非空类型且无参的公共方法定义。

文档中的例子：

**预设方法**

	SomeType getSomeType();
	Set<SomeType> getSomeTypes();
	@PortNumber int getPortNumber();

并且我们也定义了我们想注入的依赖(通过方法注入)。例子里，`AppComponent`未注入到任何地方，因为它只用作我们作用域组件的一个依赖。并且每个都定义了`inject(_Activity activity)`方法。这里我们有简单的规则 - 使用方法定义注入，该方法只有一个参数(注入到我们的依赖中)，名字无所谓，但必须返回void或者传单参数类型。

文档中的例子：

**成员注入方法**

	SomeType getSomeType();
	Provider<SomeType> getSomeTypeProvider();
	Lazy<SomeType> getLazySomeType();

**实现**

我不会涉及过多的点。相反只需要克隆[GithubClient](https://github.com/frogermcs/GithubClient)代码，并在最新的Android Studio中引入即可。这里有一些要点：

####Dagger2安装

仅需检查`/app/build.gradle`文件。我们所需做的是增加Dagger2依赖并使用[android-apt](https://bitbucket.org/hvisser/android-apt)插件来连接Android Studio IDE和生成的代码。

**AppComponent**

从`GithubClientApplication`类开始探索GithubClient工程。这里创建并保存了`AppComponent`文件。这意味着所有单例对象将与Applicaiton对象(所有时期内)同生共死。

`AppComponent`实现由Dagger 2生成的代码提供(使用构建模式创建对象：`Dagger{ComponentName}.builder()`)。而且这有集合了所有组件的依赖(模块和其他组件)。

**区域组件**

为了检查Activities组件如何创建的，只需要从`SplashActivity`开始查看。它重写了`setupActivityComponent(AppComponent)`,那里它创建了自己的组件`SplashActivityComponent`，并注入到所有`@Inject
`注解的依赖(本例是`SplashActivityPresenter`和`AnalyticsManager`)。

这里我们提供了AppComponent实例(因为`SplashActivityPresenter`依赖它)，还有`SplashActivityModule`(提供Presenter和Acitivyt实例)。

剩下的就靠你了。认真的——揣摩一切如何结合在一起。而在接下来的文章中我们会尽量密切关注Dagger2(它是如何工作的)。

\##工程的全部源码在[这里](https://github.com/frogermcs/GithubClient/tree/1bf53a2a36c8a85435e877847b987395e482ab4a)。

\###作者
[Azimo](https://azimo.com/)*移动部门总监*

如果你喜欢这个文章，你可以[分享给你的伙伴](https://twitter.com/intent/tweet?url=http://frogermcs.github.io/dependency-injection-with-dagger-2-the-api/&text=Dependency%20injection%20with%20Dagger%202%20-%20the%20API&via=froger_mcs&hashtags=AndroidDev)或者[Twitter上关注我](https://twitter.com/froger_mcs)。

*写于2015，6月10日。*