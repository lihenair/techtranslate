# Android项目使用Dagger2进行依赖注入 #

依赖注入是一种软件设计模式，致力于应用松耦合，可扩展性和可维护性。本教程中，将学到如何使用Dagger2进行依赖注入。

## 介绍 ##

当一个对象需要或依靠其他对象处理工作时，这就是一个依赖关系。依赖关系可以通过让依赖对象创建被依赖者或者使用工厂方法创建一个被依赖者来解决。在依赖注入的情况下，然而，向类提供的依赖需要避免类来创建它们。这样你创建的软件就是松耦合和高可维护的。

本教程使用Dagger的最新版，[Dagger 2](http://google.github.io/dagger/)。在写作期间，Dagger 2还未正式发布，处于pre-alpha阶段。然而，它是可用和稳定的。你可以访问[Dagger on GitHub](https://github.com/google/dagger)得到项目的新闻和正式版的发布日期。

## 前置条件

你需要在开发机上安装最新版的Android Studio，可以从[Android开发者网站](http://developer.android.com/sdk/index.html)下载。

1. ####Dagger 2 API

   Dagger 2提供了一些特殊的注解：
  - `@Module`用于类，该类的方法提供依赖。
  - `@Provides`用于`@Module`注解的类中的方法
  - `@inject`请求依赖(用在构造函数，域或方法)
  - `@Component`是模块和注入之间的接口

   这些就是即将使用Dagger 2进行依赖注入所需要了解的重要注解。我将在一个简单Android应用中向你展示如何使用它们。

2. ####Dagger 2工作流程

  为了正确使用Dagger 2，你需要遵守以下步骤：
  1. 识别依赖对象和它的依赖。
  2. 创建带`@Module`注解的类，对每个返回依赖的方法使用`@Provides`注解。
  3. 在依赖对象上使用`@Inject`注解来请求依赖。
  4. 使用`@Componet`注解创建一个接口并增加第二步中创建的带`@Module`注解的类。
  5. 创建一个`@Component`接口的对象来实例化自带依赖的依赖对象。

   依赖分析从运行时转换到编译时。这意味着在开发阶段就可以知道可能的问题，而不像其他的库，例如[Guice](https://github.com/google/guice)。在开始使用Dagger 2库之前，你需要安装Android Stuido来访问生成的类。

3. ####Android Studio环境建立

  #####Step 1
  使用Android Studio创建一个新的应用并命名。我命名我的工程为**TutsplusDagger**。
  ![](https://cms-assets.tutsplus.com/uploads/users/425/posts/23345/image/dagger-2-type-a-name-for-the-project.png)

  #####Step 2
  设置项目的**最小SDK版本**为**API 10**来适配更多机型。
  ![](https://cms-assets.tutsplus.com/uploads/users/425/posts/23345/image/dagger-2-select-minimun-sdk.png)

  #####Step 3
  创建的activity选择**空**布局。对于本教程，不需要特殊布局。
  ![](https://cms-assets.tutsplus.com/uploads/users/425/posts/23345/image/dagger-2-choose-template.png)

  #####Step 4
  命名activity为Main
Activity并点击**Finish**按钮。
  ![](https://cms-assets.tutsplus.com/uploads/users/425/posts/23345/image/dagger-2-name-for-activity.png)

  工程创建后，你需要对gradle文件进行一些修改。让我们在下一步中做这些改动。

4. 配置Gradle设置。
  #####Step 1
  我们需要修改工程的**build.gradle**文件如下：

		buildscript {
		    repositories {
		        jcenter()
		    }
		    dependencies {
		        classpath 'com.android.tools.build:gradle:1.0.0'
		        classpath 'com.neenbedankt.gradle.plugins:android-apt:1.4'
		    }
		}
		
		allprojects {
		    repositories {
		        mavenCentral()
		        maven{
		            url 'https://oss.sonatype.org/content/repositories/snapshots/'
		        }
		    }
		}

  让我们看一下做了哪些修改：
  - **dependencies**：这部分，我增加了一个插件，该插件将用于访问Dagger生成的文件。如果不加入，访问这些新类时将看到错误。
  - **allprojects**:这个修改是因为我们使用的库当前处于pre-alpha阶段，而且这是使用Maven来访问该库的唯一可用地址。也可以从Sonatype下载[Dagger](https://oss.sonatype.org/content/repositories/snapshots/com/google/dagger/dagger/2.0-SNAPSHOT/)和[Dagger编译器](https://oss.sonatype.org/content/repositories/snapshots/com/google/dagger/dagger-compiler/2.0-SNAPSHOT/)库，但本教程是基于Maven仓库创建的。

  #####Step 2
  打开工程app文件夹中的**build.gradle**文件，修改如下：

	    apply plugin: 'com.android.application'
	    apply plugin: 'com.neenbedankt.android-apt'
	 
	    android {
		    compileSdkVersion 21
		    buildToolsVersion "21.1.2"
		 
		    defaultConfig {
		        applicationId "com.androidheroes.tutsplusdagger"
		        minSdkVersion 10
		        targetSdkVersion 21
		        versionCode 1
		        versionName "1.0"
		    }
		    buildTypes {
		        release {
		            minifyEnabled false
		            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
		        }
		    }
	    }
	 
	    dependencies {
		    compile fileTree(dir: 'libs', include: ['*.jar'])
		    compile 'com.android.support:appcompat-v7:21.0.3'
		 
		    compile 'com.google.dagger:dagger:2.0-SNAPSHOT'
		    apt 'com.google.dagger:dagger-compiler:2.0-SNAPSHOT'
		    provided 'org.glassfish:javax.annotation:10.0-b28'
	    }

  在文件开头，我应用了新的插件。务必将新插件(**com.neenbedankt.android-apt**)放到Android插件之后。如果不这样做，在同步工程的gradle文件时将显示错误。

  在**dependencies**中添加了如下依赖：
  - **dagger**库
  - **dagger-compiler**用于代码生成
  - **javax.annotation**用于Dagger之外需求的额外注解

  在更新Dagger的配置后，你需要点击上面的按钮来同步工程的gradle文件。

  ![](https://cms-assets.tutsplus.com/uploads/users/425/posts/23345/image/dagger-2-gradle-sync.jpg)

  到这里，你的应用已经有了一个可以准备使用的空项目。如果有错误，请确保你正确的遵守以上步骤。现在我们来实现我们的栗子项目。

5. 实现Dagger 2
  #####Step 1：识别依赖对象
  对于本教程，我打算实现两个类，`Vehicle`和`Motor`。`Motor`是独立类，`Vehicle`是依赖类。我打算开始在包名为`model`中创建这个模型。

  `Motor`类结构如下：

    
	package com.androidheroes.tutsplusdagger.model;
	
	/**
	 * Created by kerry on 14/02/15.
	 */
	public class Motor {
	 
	    private int rpm;
	 
	    public Motor(){
	        this.rpm = 0;
	    }
	 
	    public int getRpm(){
	        return rpm;
	    }
	 
	    public void accelerate(int value){
	        rpm = rpm + value;
	    }
	 
	    public void brake(){
	        rpm = 0;
	    }
	}

  该类只有一个名为`rmp`的属性，我准备通过`accelerate`和`brake`方法来修改它。并且使用`getRpm`方法来访问当前值。

  `Vehicle`类结构如下：

	package com.androidheroes.tutsplusdagger.model;
	
	/**
	* Created by kerry on 14/02/15.
	*/
	public class Vehicle {
	 
	    private Motor motor;
	 
	    public Vehicle(Motor motor){
	        this.motor = motor;
	    }
	 
	    public void increaseSpeed(int value){
	        motor.accelerate(value);
	    }
	 
	    public void stop(){
	        motor.brake();
	    }
	 
	    public int getSpeed(){
	        return motor.getRpm();
	    }
	}

  在类中，你看到我没有创建`Motor`类的新对象，即使使用了它的方法。在真实世界的应用中，这个类应当有更多的方法和属性，但现在尽量保持简单。

  #####Step 2：创建`@Module`类

  现在要创建带`@Module`注解的类。该类将提供自带依赖的对象。因为这点，需要创建新的包名(只是为了保持顺序)，命名为`module`并在其中增加新类，代码如下：
    
	package com.androidheroes.tutsplusdagger.module;
 
	import com.androidheroes.tutsplusdagger.model.Motor;
	import com.androidheroes.tutsplusdagger.model.Vehicle;
	 
	import javax.inject.Singleton;
	 
	import dagger.Module;
	import dagger.Provides;
	 
	/**
	 * Created by kerry on 14/02/15.
	 */
	 
	@Module
	public class VehicleModule {
	 
	    @Provides @Singleton
	    Motor provideMotor(){
	        return new Motor();
	    }
	 
	    @Provides @Singleton
	    Vehicle provideVehicle(){
	        return new Vehicle(new Motor());
	    }
	}

  在**Step 1**中我指出，`Vehicle`需要`Motor`来正常工作。这就是为什么你需要创建两个提供者，一个给`Motor`(独立模型)，另一个给`Vehicle`(指明它的依赖)。

  别忘了每个提供者(或方法)必须添加`@Provides`注解并且类必须有`@Module`注解。`@Singleton`注解指明对象只能有一个实例。

  #####Step 3: 依赖对象中请求依赖

  现在不同的模型都有了提供者，你需要请求它们。就像`Vehicle`需要`Motor`那样，你需要在`Vehicle`的构造函数前增加`@Inject`注解，代码如下：

    @Inject
    public Vehicle(Motor motor){
        this.motor = motor;
    }

  你可以使用`@Inject`注解在构造函数，域，方法中来请求依赖。这个例子里，我在构造函数中使用注入。

  #####Step 4：使用`@Inject`链接`@Module`

  使用带`@Component`注解的接口连接依赖的提供者，`@Module`，和请求他们的类，这些类标记了`@Inject`注解：

    package com.androidheroes.tutsplusdagger.component;

	import com.androidheroes.tutsplusdagger.model.Vehicle;
	import com.androidheroes.tutsplusdagger.module.VehicleModule;
	 
	import javax.inject.Singleton;
	 
	import dagger.Component;
	 
	/**
	 * Created by kerry on 14/02/15.
	 */
	 
	@Singleton
	@Component(modules = {VehicleModule.class})
	public interface VehicleComponent {
	 
	    Vehicle provideVehicle();
	 
	}

  在`@Component`注解中，你需要指明打算使用哪个类 —— 本例是`VehicleModule`，前面已经创建了。如果你打算使用更多的模块，只需要使用逗号作为分隔符来增加它们。

  接口中，给每个需要的对象增加方法，它们会自动添加依赖。本例中，因为只需要一个`Vehicle`对象，所以只有一个方法。

  #####Step 5： 使用`@Component`接口获取对象

  现在万事俱备了，你需要拥有一个接口的实例并调用它的方法来获取需要的对象。我将在`MainActivity`中的`OnCreate`方法中实现，代码如下：

    package com.androidheroes.tutsplusdagger;
 
	import android.support.v7.app.ActionBarActivity;
	import android.os.Bundle;
	import android.widget.Toast;
	 
	import com.androidheroes.tutsplusdagger.component.Dagger_VehicleComponent;
	import com.androidheroes.tutsplusdagger.component.VehicleComponent;
	import com.androidheroes.tutsplusdagger.model.Vehicle;
	import com.androidheroes.tutsplusdagger.module.VehicleModule;
	 
	public class MainActivity extends ActionBarActivity {
 
    Vehicle vehicle;
 
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
 
        VehicleComponent component = Dagger_VehicleComponent.builder().vehicleModule(new VehicleModule()).build();
 
        vehicle = component.provideVehicle();
 
        Toast.makeText(this, String.valueOf(vehicle.getSpeed()), Toast.LENGTH_SHORT).show();
    }

  当你打算创建一个带`@Component`注解的接口对象时，你需要使用`Dagger_<NameOfTheComponentInterface>`前缀来实现，本例是`Dagger_VehicleComponent`，然后使用`builder`方法来调用各个模块。

  秘诀就在代码的第23行。你只要求`Vehicle`类的一个对象，Dagger2库会负责准备该对象的所有依赖。同样，你看不到其他任何对象的新实例——Dagger2库帮你处理了所有。

  现在可以在设备或者模拟器上运行应用。如果按照教程一步一步实现，你将看到一个显示`rpm`变量初始值的`Toast`消息。

  在相关的工程里，你能看到一个对`MainActivity`类定制的用户接口，该接口中，通过点击屏幕上的按钮，你可以修改`rpm`变量的值。

  ##结论

  依赖注入是一个模式，在你的应用中迟早会用到该模式。使用Dagger 2，你拥有了实现依赖注入的利器。我希望该教程对你有用，如果你喜欢它请分享它。