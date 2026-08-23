Keeping Android runtime permissions from cluttering your app (Headless Dialog Fragments!)

原文链接:[https://medium.com/android-news/keeping-android-runtime-permissions-from-cluttering-your-app-headless-dialog-fragments-6d675bf080c0#.ph9wl24e3](https://medium.com/android-news/keeping-android-runtime-permissions-from-cluttering-your-app-headless-dialog-fragments-6d675bf080c0#.ph9wl24e3)

我知道我延误了在[Stream](https://play.google.com/store/apps/details?id=com.sparc.stream)应用中实现Android运行时权限检查功能。我们自有原因，但是现在Nougat已经发布了，是时候升级我targetSdkVersion到24了。

我不是设计运行时权限的狂热粉丝。它很快就会搞乱你的activity/fragment代码，因为需要在大量场景中向用户提示适当的消息。为了解决这个问题，我决定使用headless dialog fragment包含几乎各方面的权限管理。

为了展示如何工作的，我创建了一个样例应用，它展示了如何请求所有需要的权限来录制视频(相机，麦克风和存储)。完整代码可以在这里找到:[https://github.com/tylerjroach/RuntimePermissionsExample](https://github.com/tylerjroach/RuntimePermissionsExample)。来看看CameraPermissionsDialogFragment的完整代码。

```
/**
 * Created by tylerjroach on 8/31/16.
 */

public class CameraPermissionsDialogFragment extends DialogFragment{
  private final int PERMISSION_REQUEST_CODE = 11;

  private Context context;
  private CameraPermissionsGrantedCallback listener;

  private boolean shouldResolve;
  private boolean shouldRetry;
  private boolean externalGrantNeeded;

  public static CameraPermissionsDialogFragment newInstance() {
    return new CameraPermissionsDialogFragment();
  }

  public CameraPermissionsDialogFragment() {}

  @Override public void onAttach(Context context) {
    super.onAttach(context);
    this.context = context;
    if (context instanceof CameraPermissionsGrantedCallback) {
      listener = (CameraPermissionsGrantedCallback) context;
    }
  }

  @Override public void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setStyle(STYLE_NO_TITLE, R.style.PermissionsDialogFragmentStyle);
    setCancelable(false);
    requestNecessaryPermissions();
  }

  @Override public void onResume() {
    super.onResume();
    if (shouldResolve) {
      if (externalGrantNeeded) {
        showAppSettingsDialog();
      } else if(shouldRetry) {
        showRetryDialog();
      } else {
        //permissions have been accepted
        if (listener != null) {
          listener.navigateToCaptureFragment();
          dismiss();
        }
      }
    }
  }

  @Override public void onDetach() {
    super.onDetach();
    context = null;
    listener = null;
  }

  @Override public void onRequestPermissionsResult(int requestCode,
      String permissions[], int[] grantResults) {
    shouldResolve = true;

    for (int i=0; i<permissions.length; i++) {
      String permission = permissions[i];
      int grantResult = grantResults[i];

      if (!shouldShowRequestPermissionRationale(permission) && grantResult != PackageManager.PERMISSION_GRANTED) {
        externalGrantNeeded = true;
        return;
      } else if (grantResult != PackageManager.PERMISSION_GRANTED) {
        shouldRetry = true;
        return;
      }
    }
  }

  private void requestNecessaryPermissions() {
    requestPermissions(new String[] {
        Manifest.permission.CAMERA,
        Manifest.permission.RECORD_AUDIO,
        Manifest.permission.WRITE_EXTERNAL_STORAGE}, PERMISSION_REQUEST_CODE);
  }

  private void showAppSettingsDialog() {
    new AlertDialog.Builder(context)
        .setTitle("Permissions Required")
        .setMessage("In order to record videos, access to the camera, microphone, and storage is needed. Please enable these permissions from the app settings.")
        .setPositiveButton("App Settings", new DialogInterface.OnClickListener() {
          @Override public void onClick(DialogInterface dialogInterface, int i) {
            Intent intent = new Intent();
            intent.setAction(Settings.ACTION_APPLICATION_DETAILS_SETTINGS);
            Uri uri = Uri.fromParts("package", context.getApplicationContext().getPackageName(), null);
            intent.setData(uri);
            context.startActivity(intent);
            dismiss();
          }
        })
        .setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
          @Override public void onClick(DialogInterface dialogInterface, int i) {
            dismiss();
          }
        }).create().show();
  }

  private void showRetryDialog() {
    new AlertDialog.Builder(context)
        .setTitle("Permissions Declined")
        .setMessage("In order to record videos, the app needs access to the camera, microphone, and storage.")
        .setPositiveButton("Retry", new DialogInterface.OnClickListener() {
          @Override public void onClick(DialogInterface dialogInterface, int i) {
            requestNecessaryPermissions();
          }
        })
        .setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
          @Override public void onClick(DialogInterface dialogInterface, int i) {
            dismiss();
          }
        }).create().show();
  }

  public interface CameraPermissionsGrantedCallback {
    void navigateToCaptureFragment();
  }
}
```
在onCreate()中，我们调用了requestNecessaryPermissions()。它提示用户拒绝/允许每个请求的权限，结果传递到onRequestPermissionResult()。例子里，我们检查了3个可能的场景：

* 允许所以权限
* 拒绝一个或多个权限
* 拒绝一个或多个权限，并勾选"不再弹出"

无论结果如何，你在onRequestPermissionsResult()中做更新时都会小心考虑。结果传递到这个方法，而应用处在暂停状态。结果，特定操作导致一个崩溃(例如，FragmentTransaction commit时会有IllegalStateException)。为了解决这个，我对操作设置了布尔标志，并且一旦应用返回前台，重写了onResume()来处理这个操作。这样保证了fragment切换安全运行，ui会安全更新。

现在回到请求运行时权限的activity。你能看到activity只负责检查打开相机之前是否需要任何权限。你可以看到如果没有用DialogFragment分离权限请求，activity代码会迅速变乱。

```
@Override protected void onResume() {
  super.onResume();
  if (isPermissionGranted()) {
    status.setText("All permissions granted. Ready to open Camera");
  } else {
    status.setText("Permissions Needed");
  }
}

@Override public void navigateToCaptureFragment() {
  if (isPermissionGranted()) {
    Toast.makeText(this, "Opening Camera!", Toast.LENGTH_LONG).show();
  } else {
    CameraPermissionsDialogFragment.newInstance().show(getSupportFragmentManager(), CameraPermissionsDialogFragment.class.getName());
  }
}

private boolean isPermissionGranted() {
  return ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED &&
      ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED &&
      ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE) == PackageManager.PERMISSION_GRANTED;
}
```
旁注：

* 使用DialogFragment，然而，一个标准的Headless Fragment也可以工作。我选择使用DialogFragment因为setCancelable(false)可以轻松地阻止所有外部触摸，还有使用show()和dismiss()就可以简单的创建/销毁。
* 默认的，DialogFragment使屏幕背景内容变暗。为了移除这个，可在对话框中使用简单的样式。

```
<style name="PermissionsDialogFragmentStyle" parent="Base.Theme.AppCompat.Dialog">
  <item name="android:backgroundDimEnabled">false</item>
</style>
```
我期待你的评论和问题。如果这篇文对你有帮助，请点❤