#产品使用Dagger 2——减少方法数

**Dagger 2**——完全静态，编译时依赖注入框架是[Azimo](https://play.google.com/store/apps/details?id=com.azimo.sendmoney) Android应用的代码架构骨干。我们已经知道，随着开发团队的增长，干净的代码结构是每个项目中最重要的事情之一。初始化/使用分离，更以测试(单元或功能),更好扩展——这些只是引入如Dagger 2依赖注入框架的一小部分好处。

现在我们可以找到许多教程和代码例子展示如何在Android中开始使用Dagger2和依赖注入。如果这是你寻找的，这是我的系列博客可以帮助你：
- [介绍依赖注入](http://frogermcs.github.io/dependency-injection-with-dagger-2-introdution-to-di/)
- [Dagger 2 API](http://frogermcs.github.io/dependency-injection-with-dagger-2-the-api/)
- [Dagger 2——定制范围](http://frogermcs.github.io/dependency-injection-with-dagger-2-custom-scopes/)
- [Dagger 2——图形创建性能](http://frogermcs.github.io/dagger-graph-creation-performance/)
- [使用Dagger2进行依赖注入——生产者](https://medium.com/@froger_mcs/dependency-injection-with-dagger-2-producers-c424ddc60ba3#.o9ks10hzp)
- [Dagger2使用RxJava进行异步注入](https://medium.com/@froger_mcs/async-injection-in-dagger-2-with-rxjava-e7df503343c0#.5vuheb5ui)
- [注入万物——ViewHolder和Dagger2(使用Multibinding和AutoFactor的例子)](https://medium.com/@froger_mcs/inject-everything-viewholder-and-dagger-2-e1551a76a908#.ojfwmz35r)

但这些只展示如何开始使用DI。这也是在我们app中使用两年后，为什么今天打算开始分析使用Dagger2的经验。

###@Component vs @Subcomponent
自定义范围在简单教程中通常解释不清楚，但它是Dagger2最强有力功能之一。在更复杂的app中只使用**@Singleton**不会让你的工作更简单。

让我们考虑一个简单的例子——我们有严格连接当前登录用户的依赖(例如，***UserProfilePresenter***类负责用户配置屏幕的逻辑)。当我们需要用户实体时，不需要每次都调用数据存储，我们可以创建***@User***范围，并将所有依赖保持在单一实例***UserComponent***中，该实例生命周期与登陆的用户一致。

> 在生成app中使用自定义范围不是这篇文字的主题，但我们会在接下来讲解它。

在Dagger2，我没有两种方式构建自定义范围和组件来继承并扩展对象图：

- 我们可以构建另一个***@Component***来明确展示扩展***Component***(本例的***AppComponent***)

```
@UserScope
@Component(
    modules = UserModule.class,
    dependencies = AppComponent.class
)
public interface UserComponent {
    UserProfileActivity inject(UserProfileActivity activity);
}
```
- 或者我们可以定义***@Subcomponent***，它是从基础组件的抽象工厂方法([阅读更多](http://google.github.io/dagger/api/latest/dagger/Component.html#subcomponents))创建的：

```
@UserScope
@Subcomponent(
    modules = UserModule.class
)
public interface UserComponent {
    UserProfileActivity inject(UserProfileActivity activity);
}

//===== AppComponent.java =====

@Singleton
@Component(modules = {...})
public interface AppComponent {
    // Factory method to create subcomponent
    UserComponent plus(UserModule module);
}
```

###这两种方法的区别？

[文档](http://google.github.io/dagger/api/latest/dagger/Component.html#component-dependencies)讨论了依赖可视性的区别。***@Subcomponent***从它的父类访问所有依赖，而***@Component***只能访问在基类***@Component***接口暴露的公共性的依赖。

考虑到这点，我们最初选择带依赖***@Component***的方法。工程的所有组件都依赖范围是***@Singleton***的***AppComponent***。

###当出现方法数事情...
但在***@Component***和***@Subcomponent***之间有另一个重要的不同。让我们看看生成的代码。子组件的实现只是基础组件的一个内部类。所以对于依赖**AppCompoenet**生成代码的**UserProfiileActivityComponent**可能长这样：

```
public final class DaggerAppComponent implements AppComponent {

    //...AppComponent code...

    private final class UserProfileActivityComponentImpl implements UserProfileActivityComponent {
        private final UserProfileActivityComponent.UserProfileActivityModule userProfileActivityModule;
        private Provider<UserProfileActivity> provideActivityProvider;
        private Provider<UserProfileActivityPresenter> userProfileActivityPresenterProvider;
        private MembersInjector<UserProfileActivity> userProfileActivityMembersInjector;

        private UserProfileActivityComponentImpl(
            UserProfileActivityComponent.UserProfileActivityModule userProfileActivityModule) {
            this.userProfileActivityModule = Preconditions.checkNotNull(userProfileActivityModule);
            initialize();
        }

        private void initialize() {
            this.provideActivityProvider = DoubleCheck.provider(BaseActivityModule_ProvideActivityFactory.create(userProfileActivityModule));

            this.userProfileActivityPresenterProvider = DoubleCheck.provider(
                UserProfileActivityPresenter_Factory.create(
                    MembersInjectors.<UserProfileActivityPresenter>noOp(),
                    provideActivityProvider,
                    DaggerAppComponent.this.logoutManagerProvider,
                    DaggerAppComponent.this.userManagerProvider)
            );

            this.userProfileActivityMembersInjector = UserProfileActivity_MembersInjector.create(
                DaggerAppComponent.this.logoutManagerProvider,
                DaggerAppComponent.this.userManagerProvider
                userProfileActivityPresenterProvider)
            );
        }

        @Override
        public UserProfileActivity inject(UserProfileActivity activity) {
            userProfileActivityMembersInjector.injectMembers(activity);
            return activity;
        }
    }
}
```

20-31行展示了Dagger如何提供从*AppComponent*到*UserProfileActivityComponent*的依赖。子组件可访问基础组件提供的域，所以它们可以直接使用。

不同情况取决于***@Component***。相同的结构(***UserProfileActivityComponent***依赖***AppComponent***)将生成这样的代码：

```
public final class DaggerUserProfileActivityComponent implements UserProfileActivityComponent {
    private Provider<LogoutManager> logoutManagerProvider;
    private Provider<UserManager> userManagerProvider;

    //...

    private DaggerUserProfileActivityComponent(Builder builder) {
        assert builder != null;
        initialize(builder);
    }

    @SuppressWarnings("unchecked")
    private void initialize(final Builder builder) {
        this.logoutManagerProvider = new Factory<LogoutManager>() {
            private final AppComponent appComponent = builder.appComponent;

            @Override
            public LogoutManager get() {
                return Preconditions.checkNotNull(
                    appComponent.getLogoutManager(),
                    "Cannot return null from a non-@Nullable component method");
            }
        };

        this.userManagerProvider = new Factory<UserManager>() {
            private final AppComponent appComponent = builder.appComponent;

            @Override
            public UserManager get() {
                return Preconditions.checkNotNull(
                    appComponent.getUserManager(),
                    "Cannot return null from a non-@Nullable component method");
            }
        };

        //... more providers ....
        
    }

    @Override
    public UserProfileActivity inject(UserProfileActivity activity) {
        userProfileActivityMembersInjector.injectMembers(activity);
        return activity;
    }

    //...
}
```

14-34行展示了每个从***AppComponent***发出的依赖请求都需要自己的方法来生成***Provider<>***对象。为什么？因为依赖组件只能访问那些基类组件暴露了公共接口的依赖。

这对我们意味着什么——Android开发者？从基类组件带到依赖组件中的每一个依赖都讲都让我们更接近65k方法数限制：

因为这一点，我们决定所有依赖于***@Component***都迁移到***@SubComponent***。经过这样处理，我们减少了大约5000个额外的方法。

###快速分析你的APK

最后值得一提的是从**Android Studio 2.2**开始出现了一个新的功能，让我们分析APK文件。访问方式是**Build -> Analyze APK**...

![](https://cdn-images-1.medium.com/max/1600/1*LX37WOAZPGsx9W73P879zg.png)

这个工具允许我们检查特殊组件的大小(类，资源等)，和最能帮助我们的——得到.dex文件的基础信息(类/方法数)。这是依赖注入优化的起始点。

今天就到这里了，但保持联系。不久，我们将分享更多关于Dagger2和依赖注入的经验。感觉阅读！

想了解更多？关注我们的Twitter[@AzimoLabs](https://twitter.com/azimolabs)和[Github账号](https://github.com/azimolabs)。