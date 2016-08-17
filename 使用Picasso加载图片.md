一图胜千言。对于许多app也是一样的。为了使图片加载轻松无忧，我推荐使用图片加载库。个人偏爱Square发布的[Picasso](http://square.github.io/picasso/)库。无论是显示下载图片的占位符，或者缩放缓存图片，一库搞定。要使用Picasso，需要在你模块的gradle.build文件中增加这个依赖：
    
    compile 'com.squareup.picasso:picasso:2.5.2'

好了。万事俱备。让我们加载图片到**ImageView**中：

    Picasso.with(context.getApplicationContext())
      .load(url)
      .placeholder(R.drawable.img_placeholder)
      .error(R.drawable.img_error)
      .into(imageView);

使用这段代码，在下载图片时会显示默认图片。随后这张图片会消失。如果下载时发生错误，将显示错误图片。这是Picasso的基本用法。不过库里还有许多高级功能。使用.fit()函数，Picasso自动缩放图片来适应**ImageView**的尺寸，这样有效的使用了内存。此外，你可以使用.resize(width, heigth)函数来手动缩放图片 —— 这里还可以用.onlyScaleDown()。对于缩放，库还提供了.centerCrop()和.centerInside()方法。

另一个不错的功能可能是滚动时暂停图片下载。这是通过添加滚动标签实现的，标签可以到请求。例如，可以使用下面的RecyclerView.OnScrollListener：

    public class PicassoOnScrollListener extends RecyclerView.OnScrollListener {
	    public static final Object TAG = new Object();
	    private static final int SETTLING_DELAY = 500;
	    
	    private static Picasso sPicasso = null;
	    private Runnable mSettlingResumeRunnable = null;
	     
	    public PicassoOnScrollListener(Context context) {
		    if(this.sPicasso == null) {
		    	this.sPicasso = Picasso.with(context.getApplicationContext());
		    }
	    }
	     
	    @Override
	    public void onScrollStateChanged(RecyclerView recyclerView, int scrollState) {
		    if(scrollState == RecyclerView.SCROLL_STATE_IDLE) {
			    recyclerView.removeCallbacks(mSettlingResumeRunnable);
			    sPicasso.resumeTag(TAG);
		     
		    } else if(scrollState == RecyclerView.SCROLL_STATE_SETTLING) {
			    mSettlingResumeRunnable = new Runnable() {
			    @Override
			    public void run() {
			    sPicasso.resumeTag(TAG);
			    }
			    };
			     
			    recyclerView.postDelayed(mSettlingResumeRunnable, SETTLING_DELAY);
			     
		    } else {
		    	sPicasso.pauseTag(TAG);
		    }
	    }
    }

给recyclerView.addOnScrollListener(new PicassoOnScrollListener(context))；增加监听者 —— 现在，如果为图片请求增加.tag(PicassoOnScrolllistener.TAG)，当用户滚动RecyclerView时，图片加载将暂停。

启用日志进行调试也方便了。此外，你可能为了低内存设备修改bitmap配置为RGB_565以较低的图片质量成本来防止发生OutOfMemoryError异常，。可以通过在Application类中构建自定义的Picasso实例来实现。

	public class MyApplication extends Application {
	    @Override
	    public void onCreate() {
	        super.onCreate();
	 
	        Picasso.Builder picassoBuilder = new Picasso.Builder(this);
	        if(BuildConfig.DEBUG) { picassoBuilder.loggingEnabled(true); }
	        if(isLowMemoryDevice()) { picassoBuilder.defaultBitmapConfig(Bitmap.Config.RGB_565); }
	        
	        Picasso.setSingletonInstance(picassoBuilder.build());
	    }
	 
	    private boolean isLowMemoryDevice() {
	        if(Build.VERSION.SDK_INT >= 19) {
	            return ((ActivityManager) getSystemService(ACTIVITY_SERVICE)).isLowRamDevice();
	        } else {
	            return false;
	        }
	    }
	}