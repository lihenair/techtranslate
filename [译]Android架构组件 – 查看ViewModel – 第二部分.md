原文链接:[https://riggaroo.co.za/android-architecture-components-looking-viewmodels-part-2/](https://riggaroo.co.za/android-architecture-components-looking-viewmodels-part-2/)

如果你回忆上一篇文章，下图指出了我们将如何组织我们的“日期倒计时”应用。

![](https://i0.wp.com/riggaroo.co.za/wp-content/uploads/2017/05/MVVM-using-the-new-android-architecture-components-1.png?ssl=1)

本文我们将创建上图显示的`EventListViewModel`和`AddEventViewModel`。可在[这篇文章](https://github.com/riggaroo/android-arch-components-date-countdown)找到所有源码。在开始创建`ViewModels`之前，我们需要首先看看什么是`ViewModel`。

### 什么是ViewModel？
`ViewModel`既不是新的概念，也不是Android的概念。 名`ViewModel`来自于2005年左右的Microsoft设计的[MVVM](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93viewmodel)模式。新的架构组件中，一个新类是`ViewModel`类。

`ViewModel`负责为`View`**准备数据**。它们将数据暴露给正在监听更改的任何视图。在Android中，使用`ViewModel`类时应该记住一些具体的事实：

* `ViewModel`可以在Activity配置更改中**保留其状态**。它保存的数据立即可用于下一个Activity实例，而**不**需要在`onSaveInstanceState()`中保存数据，并手动还原。
* `ViewModel`与特定的Activity或Fragment实例无关。
* `ViewModel`允许在Fragment之间轻松**共享**数据（意味着您不再需要通过ctivity来协调动作）。
* `ViewModel`将保持在内存中，直到`Lifecycle`的**范围**永远消失 - Activity调用finish; 在Fragment调用ditached。
* 因为`ViewModel`独立于Activity或Fragment实例，它不直接引用其中的任何View或保持上下文的引用。真会导致[内存泄漏](https://riggaroo.co.za/fixing-memory-leaks-in-android-outofmemoryerror/)。
* 如果`ViewModel`需要应用的上下文(例如查找系统服务)，它可继承`AndroidViewModel`类，并有一个构造函数来接收Application实例。

### 创建ViewModel

#### EventListViewModel
`EventListViewModel`类用于打开日期倒计时应用打开时展示事件列表。

1. 创建名为`EventListViewModel`的类。确保它从架构组件类继承`ViewModel`。类中，我们打算将之前放在`EventListFragment`中的代码迁移到`ViewModel`中。
2. `EventListViewModel`中添加`LiveData`变量。EventRepository变量使用Dagger注入。`EventListViewModel`现在长这样：

	```java
	public class EventListViewModel extends ViewModel implements CountdownComponent.Injectable {
 
    	private LiveData<List<Event>> events = new MutableLiveData<>();
  
    	@Inject
    	EventRepository eventRepository;
 
    	@Override
    	public void inject(CountdownComponent countdownComponent) {
        	countdownComponent.inject(this);
        	events = eventRepository.getEvents();
    	}
 
    	public LiveData<List<Event>> getEvents() {
        	return events;
    	}
	}
	```
	
3. 现在在`EventListFragment`中，我们打算使用`ViewModel`替换事件加载代码:

	```java
	public class EventListFragment extends LifecycleFragment {
  
   		private EventListViewModel eventListViewModel;
  
    	@Nullable
    	@Override
    	public View onCreateView(LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        	//.. inflate view etc
        	eventListViewModel = ViewModelProviders.of(this, new CountdownFactory(countdownApplication).get(EventListViewModel.class);
      
        	eventListViewModel.getEvents().observe(this, events -> {
            	adapter.setItems(events);
        	});
        	return v;
    	}
	}
    ```
	包含`ViewModelProvider.of(..)`的行将创建一个新的`EventListViewModel`类（如果不存在），或者它将获取存在于定义的作用域(在这种情况下是`EventListFragment`)的类。这是**神奇**的地方。当设备旋转并且Fragment被重新创建时，将在此处返回的`ViewModel`是之前使用的。这允许我们保留屏幕的状态，而无需手动将信息保存到`Bundle`并自己恢复。
	事件数据现在从`EventListViewModel`获取。如前所述，通过将其作为第一个参数，`LiveData` observable将自动为您管理。这意味着当Fragment不再使用时，Fragment将会处理可观察物。如果Fragment未启动或恢复，则不可调用observable回调。

4. 创建一个Dagger组件`CountdownComponent`。我们将使用它来注入`ViewModel`的依赖。

	```java
	@Singleton
@Component(modules = {CountdownModule.class})
public interface CountdownComponent {
 
    	void inject(EventListViewModel eventListViewModel);
 
    	void inject(AddEventViewModel addEventViewModel);
 
    	interface Injectable {
        	void inject(CountdownComponent countdownComponent);
    	}
	}
	```

5. 创建自定义`ViewModelProvider.NewInstanceFactory`用于实例化`ViewModel`。当`ViewModelProvider`需要创建新的`ViewModel`实例，它将调用工厂类的`create`方法。

	```java
	public class CountdownFactory extends ViewModelProvider.NewInstanceFactory {
 
    	private CountdownApplication application;
 
    	public CountdownFactory(CountdownApplication application) {
        	this.application = application;
    	}
 
    	@Override
    	public <T extends ViewModel> T create(Class<T> modelClass) {
        	T t = super.create(modelClass);
        	if (t instanceof CountdownComponent.Injectable) {
            	((CountdownComponent.Injectable) t).inject(application.getCountDownComponent());
        	}
        	return t;
    	}
	}
	```

6. 删除`Event`，可以在`ViewModel`中添加一个方法。该方法委托`EventRepository`删除事件。本例中，使用Rxjava来代理后台线程。

	```java
	public class EventListViewModel extends ViewModel implements CountdownComponent.Injectable {
    //.. 
    public void deleteEvent(Event event) {
        eventRepository.deleteEvent(event)
                .subscribeOn(Schedulers.io())
                .observeOn(AndroidSchedulers.mainThread())
                .subscribe(new CompletableObserver() {
                    @Override
                    public void onSubscribe(Disposable d) {
                    }
 
                    @Override
                    public void onComplete() {
                        Timber.d("onComplete - deleted event");
                    }
 
                    @Override
                    public void onError(Throwable e) {
                        Timber.e("OnError - deleted event: ", e);
                    }
                });
    	}
	}
	```

在Fragment中，我们使用委托给ViewModel的删除方法：

```java
View.OnClickListener deleteClickListener = v -> {
        Event event = (Event) v.getTag();
        eventListViewModel.deleteEvent(event);
};
```

对于`AddEventViewModel`的实现，查看完整代码[示例](https://github.com/riggaroo/android-arch-components-date-countdown)。

### 总结
新的Android架构组件解决了我们以前无法处理的常见情况。现在通过使用`ViewModel`和`ViewModelProvider`来处理屏幕旋转非常简单。

### 参考

* [ViewModel文档](https://developer.android.com/topic/libraries/architecture/viewmodel.html)
* [Android架构组件文档](https://developer.android.com/topic/libraries/architecture/index.html)
* [日期倒计时应用-完整代码](https://github.com/riggaroo/android-arch-components-date-countdown)
* [Dagger2 测试实例](http://blog.sqisland.com/2015/04/dagger-2-espresso-2-mockito.html)
