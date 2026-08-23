原文链接:[https://riggaroo.co.za/android-architecture-components-looking-room-livedata-part-1/](https://riggaroo.co.za/android-architecture-components-looking-room-livedata-part-1/)

### 新的架构组件是什么？
架构组件的基本框架包括：

* Room - 一个SQLite对象映射器。非常类似于其他库，如[ORMlite](http://ormlite.com/)或[greenDAO](http://greenrobot.org/greendao/)。它使用SQL，同时仍然允许对查询的编译时保证。
* LiveData - 一个Lifecycle可观察的核心组件。
* ViewModel - 应用程序的其他部分与Activities/Fragmets通讯点。它们与UI代码无关。
* Lifecycle - 架构自检的核心部分，它包含组件(例如一个Activity)的生命状态信息。
* LifecycleOwner - 具有Lifecycle(Activity，Fragment，Process，自定义组件)的组件的核心接口。
* LifecycleObserver - 指定出发某些生命周期方法是应该发生的情况。创建LifecycleObserver允许组件自包含。

### 使用新架构组件构建应用
我们将构建一个应用程序，该应用程序是您添加到应用程序的不同事件的倒计时。 我们将使用MVVM模式。

![](https://i1.wp.com/riggaroo.co.za/wp-content/uploads/2017/05/android_architecture_components_datecountdown.gif?resize=167%2C300&ssl=1)

下图说明了使用新架构组件构建的Android应用程序的结构。该图详细说明了我们将在本系列中构建的“日期倒计时”应用程序的最终结果。 它还指出哪些架构组件在应用程序的哪个部分中使用。

![](https://i0.wp.com/riggaroo.co.za/wp-content/uploads/2017/05/MVVM-using-the-new-android-architecture-components-1.png?resize=768%2C448&ssl=1)

MVP和MVVM之间的主要区别在于，MVVM ViewModels公开数据，有兴趣的方面可以收听该数据（或忽略它），而使用MVP，View和Presenter之间存在严格的绑定。使用MVP，它们更难以重复使用Presenters，因为它们与View紧密耦合。使用MVVM，Views可以从ViewModel订阅他们感兴趣的数据。

### 什么是Room？
Room是Android应用一种新的创建数据库方式。Room**删除**了大量之前用于存储数据的**重复代码**。Roon是一个介于Java类和SQLite的[ORM](https://en.wikipedia.org/wiki/Object-relational_mapping)。使用Room，你不再需要用到`Cursors`和`Loaders`。Room不是一个完整的ORM，例如，不能像其他ORM解决方案那样提供对象的复杂嵌套。

Room提供了集中不同的查询数据的方式：

* 可以订阅发射事件流的`LiveData`类来接收更新。课用在主线程，因为它是**异步的**。
* 使用RxJava2的`Flowable`抽象类。
* 将同步调用放在后台线程，例如`AsyncTask`。

### 开始使用Room
完整代码[在此](https://github.com/riggaroo/android-arch-components-date-countdown)

1. 在Android Studio中创建一个带默认空Activity的新工程。
2. 在顶级build.gradle中添加Google Maven仓库：
	
	```java
	allprojects {
   		repositories {
        	maven { url 'https://maven.google.com' }
        	jcenter()
    	}
	}
	```
3. 在`app/build.gradle`中添加Roomd依赖：
	
	```java
	compile "android.arch.lifecycle:extensions:1.0.0-alpha1"
	compile "android.arch.persistence.room:runtime:1.0.0-alpha1"
	annotationProcessor "android.arch.lifecycle:compiler:1.0.0-alpha1"
annotationProcessor "android.arch.persistence.room:compiler:1.0.0-alpha1"
   ```
4. 创建一个名为`Event`的实体。表单将存储事件列表。使用`@Entity`注解和表名标注这个类。id域标记`@PrimaryKey`注解，选项`autoGenerate`域设置为true。然后，Room将自动使用对象中定义的所有域创建表。

	```java
	@Entity(tableName = TABLE_NAME)
	public class Event {
   		public static final String TABLE_NAME = "events";
   		public static final String DATE_FIELD = "date";
 
   		@PrimaryKey(autoGenerate = true)
   		private int id;
   		private String name;
   		private String description;
   		@ColumnInfo(name = DATE_FIELD)
   		private LocalDateTime date;

   		public Event(int id, String name, String description, LocalDateTime date) {
       	this.id = id;
       	this.name = name;
       	this.description = description;
       	this.date = date;
   		}
 
   		public int getId() {
      		return id;
   		}
 
   		public String getName() {
       	return name;
   		}
 
   		public String getDescription() {
          return description;
   		}
 
   		public LocalDateTime getDate() {
       	return date;
   		}
 
   		@Override
   		public String toString() {
       	return "Event{" +
               "id=" + id +
               ", name='" + name + '\'' +
               ", description='" + description + '\'' +
               ", date=" + date +
               '}';
   		}
 
   		public long getDaysUntil() {
       	return ChronoUnit.DAYS.between(LocalDateTime.now(), getDate());
   		}
	}
	```
	
5. 通过创建一个名为`EventDao`的接口创建[数据访问对象](https://en.wikipedia.org/wiki/Data_access_object)(或者DAO)。使用`@Dao`注解标记这个类。然后，Room将生成一个类实现，实现接口中定义的方法(非常类似于Retrofit的工作原理)。我们可以在这里使用不同的注释，如@Query，@Delete，@Insert，@Update等注释。@Query注释可以采用SQL结构化查询。这些注解很大的一部分是编译时检查脚本。例如：如果您不正确地键入表的名称，则Room将不允许编译应用程序，直到修改正确。

	```java
	@Dao
	public interface EventDao {
 
   		@Query("SELECT * FROM " + Event.TABLE_NAME + " WHERE " + Event.DATE_FIELD + " > :minDate")
   		LiveData<List<Event>> getEvents(LocalDateTime minDate);
 
   		@Insert(onConflict = REPLACE)
   		void addEvent(Event event);
 
   		@Delete
		void deleteEvent(Event event);
 
   		@Update(onConflict = REPLACE)
   		void updateEvent(Event event); 
   	}
	```
	
6. 创建一个名为`EventDatabase`的抽象类，它将连接创建的不同实体(或表单)。这个类继承`RoomDatabase`。

	```java
	@Database(entities = {Event.class}, version = 1)
	@TypeConverters(DateTypeConverter.class)
public abstract class EventDatabase extends RoomDatabase {
   		public abstract EventDao eventDao();
	}
	```
你注意到抽象方法`eventdao()`返回刚创建的`EventDao`。Room在运行时返回正取的类实例。

	值得注意的是，`@TypeConverters(DateTypeConverter.class)`注解自动将`LocalDateTime`对象日期序列化为其String格式，并将其从存储器读取时将其反序列化为`LocalDateTime`对象。 以下是`DateTypeConverter`类的示例类定义：

	```java
	public class DateTypeConverter {

    	@TypeConverter
    	public static LocalDateTime toDate(Long timestamp) {
       	//.. convert
    	}
 
    	@TypeConverter
    	public static Long toTimestamp(LocalDateTime date) {
      		//.. convert
    	}
	}
	```

7. 使用`Room.databaseBuilder(...)`创建一个单例`EventDatabase`对象。也可以使用`Room.inMemoryDatabaseBuilder(...)'创建一个内存数据库。可以用[Dagger](https://google.github.io/dagger/)轻松地做到这一点，或者手动创建单例。使用Dagger，我们的模块如下(有关更多信息，请参阅完整的源代码)：

	```java
	@Module
public class CountdownModule {
 
   		private CountdownApplication countdownApplication;
 
   		public CountdownModule(CountdownApplication countdownApplication) {
       	this.countdownApplication = countdownApplication;
   		}
 
   		@Provides
   		Context applicationContext() {
       	return countdownApplication;
   		}
 
   		@Provides
   		@Singleton
   		EventRepository providesEventRepository(EventDatabase eventDatabase) {
       	return new EventRepositoryImpl(eventDatabase);
   		}
 
   		@Provides
   		@Singleton
   		EventDatabase providesEventDatabase(Context context) {
       	return Room.databaseBuilder(context.getApplicationContext(), EventDatabase.class, "event_db").build();
   		}
	}
	```

现在有了添加，查询和删除条目的结构，我们可以使用它们，并讨论上面定义的`EventDao`中使用的`LiveData`类。

### 什么是LiveData？
LiveData允许您在应用程序的多个组件中观察数据的更改，而不会在它们之间创建明确的和严格的依赖路径。LiveData将识别Activity和Fragment的不同生命周期。当`LiveData`与Room结合使用时，应用将自动收到数据库更新，而这些更新很难使用标准`SQLiteDatabase`来实现。

1. 创建一个名为`EventListActivity`的Activity和`EventListFragment`的Fragment。在Activity中得到Fragment。确保你的Fragment继承`LifecycleFragment`
2. 在Fragment中，添加RecyclerView，`[EventAdapter]()`，`[EventViewHoler]()`，用于显示事件列表。
3. 在Fragment中，我们可以轻松的得到`EventDatabase`引用，以及观察到数据库增加了新的条目。在可观察的回调中，可以接着设置条目到adapter中。可以使用Dagger注入`EventDatabase`。

	```java
	eventDao = eventDatabase.eventDao();
	eventDao.getEvents().observe(this, events -> {
     Log.d(TAG, "Events Changed:" + events);
     adapter.setItems(events);
});
	```

通过传递的第一个参数`this`，可观察的`LiveData`将自动被管理。这意味着当Fragment不再使用时，Fragment将处理可观测性的部署。`LiveData`类是`LivecycleOberver`的一个实例。当生命周期处于`Lifecycle.State.DESTROYED`状态时，它自动停止发送更新，而生命周期处于`Lifecycle.State.STARTED`状态时，它重新发送更新。

### 使用Room添加新事件
1. 创建一个Fragment包含两个`EditText`域，一个日期选择器和一个报错`Button`。
2. 保存按钮的`onClickListener`调用`eventDatabase.eventDao().addEvent()`就可以写入事件数据库。

	```java
	String eventTitle = editTextTitle.getText().toString();
String eventDescription = editTextDescription.getText().toString();
Event event = new Event(0, eventTitle, eventDescription, eventDateTime);
eventDatabase.eventDao().addEvent(event); //Run this in a background thread.
	```
现在我们可以访问数据库，并且可以通过UI轻松地插入或查询数据库。

![](https://i1.wp.com/riggaroo.co.za/wp-content/uploads/2017/05/android_architecture_components_datecountdown.gif?ssl=1)

### 总结
Room是一个在Android平台中封装SQLite实现的易于使用的库。它还提供了一个直观的接口来处理对象而不是`Cursor`或`ContentProviders`。 使用`LiveData`的`Room`是魔法真正发生的地方。它允许通过数据更改通知视图，这可能难以用标准的SQLiteDatabase来实现。

直接在Activity或Fragment中加载数据有一些缺陷。主要问题是Activity或Fragment与数据库紧密耦合。如果要添加测试或在另一个地方重用逻辑，这不是一个好办法。将数据库逻辑与View逻辑分开是一种更好的方法。`ViewModel`架构组件旨在解决这个问题。在[**下一篇博客文章**](https://riggaroo.co.za/android-architecture-components-looking-viewmodels-part-2/)中，我们将介绍如何使用`ViewModel`和`ViewModelProvider`来更好地按照开始时详细介绍的图表构建我们的倒计时应用程序。

### 参考
* [An Opinionated Guide to Architecting Mobile Apps](https://developer.android.com/topic/libraries/architecture/guide.html)
* [Room文档](https://developer.android.com/topic/libraries/architecture/room.html)
* [LiveData文档](https://developer.android.com/topic/libraries/architecture/livedata.html)
* [本系列第二部分](https://riggaroo.co.za/android-architecture-components-looking-viewmodels-part-2/)