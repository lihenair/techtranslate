# 使用DiffUtil更新RecyclerView的智能方式

原文链接:[https://android.jlelse.eu/smart-way-to-update-recyclerview-using-diffutil-345941a160e0](https://android.jlelse.eu/smart-way-to-update-recyclerview-using-diffutil-345941a160e0)

### 现在与notifyDataSetChanged()...说再见吧

我们在任何日常开发中经常使用`List`。当用户滚动列表时，还需要更新列表数据。为了实现这一点，我们经常从服务器获取数据，并更新接收的项目。

如果在此过程中存在些许延迟，则会影响用户体验，因此我们希望尽快完成此操作，同时减少使用的资源。

当列表的内容被改变时，我们必须调用`notifyDataSetChanged()`来获取更新，但是这是非常昂贵的。在使用`notifyDataSetChanged()`的情况下，需要多次遍历来完成工作。

这里有`DiffUtil`类，Android开发了这个工具类来处理`RecyclerView`的数据更新。

### 什么是DiffUtil
截至24.2.0，`RecyclerView`支持库，v7包提供了非常方便的实用工具类，名为`DiffUtil`。 该类找到两个列表之间的差异，并将更新的列表作为输出。此类用于通知`RecyclerView`适配器更新。

它使用Eugene W. Myers的差分算法来计算最小数量的更新。

### 如何使用？
`DiffUtil.Callback`是一个抽象类，由`DiffUtil`用作回调类，同时计算两个列表之间的差异。 它有四种抽象方法和一种非抽象方法。 你必须扩展它并覆盖所有的方法：

* getOldListSize()-返回旧列表的大小。
* getNewListSize()-返回新列表的大小。
* areItemsTheSame(int oldItemPosition, int newItemPosition)–它决定是否两个对象代表相同的条目。
* areContentsTheSame(int oldItemPosition, int newItemPosition)–它决定是否两个对象有相同的数据。这个方法只有` areItemsTheSame()`返回true时才被`DiffUtil`调用。
* getChangePayload(int oldItemPosition, int newItemPosition)–如果`areItemTheSame()`返回true，`areContentsTheSame()`返回false，那么`DiffUtil`工具调用这个方法来得到变化的结果。

下面是一个简单的`Employee`类，它在`EmployeeRecyclerViewAdapter`和`EmployeeDiffCallback`中使用，用于对员工列表进行排序。

```java

public class Employee {
    public int id;
    public String name;
    public String role;
}
```

这里是`Diff.Callback`类的实现，你可以注意到`getChangePayload()`不是抽象方法。

```java
public class EmployeeDiffCallback extends DiffUtil.Callback {

    private final List<Employee> mOldEmployeeList;
    private final List<Employee> mNewEmployeeList;

    public EmployeeDiffCallback(List<Employee> oldEmployeeList, List<Employee> newEmployeeList) {
        this.mOldEmployeeList = oldEmployeeList;
        this.mNewEmployeeList = newEmployeeList;
    }

    @Override
    public int getOldListSize() {
        return mOldEmployeeList.size();
    }

    @Override
    public int getNewListSize() {
        return mNewEmployeeList.size();
    }

    @Override
    public boolean areItemsTheSame(int oldItemPosition, int newItemPosition) {
        return mOldEmployeeList.get(oldItemPosition).getId() == mNewEmployeeList.get(
                newItemPosition).getId();
    }

    @Override
    public boolean areContentsTheSame(int oldItemPosition, int newItemPosition) {
        final Employee oldEmployee = mOldEmployeeList.get(oldItemPosition);
        final Employee newEmployee = mNewEmployeeList.get(newItemPosition);

        return oldEmployee.getName().equals(newEmployee.getName());
    }

    @Nullable
    @Override
    public Object getChangePayload(int oldItemPosition, int newItemPosition) {
        // Implement method if you're going to use ItemAnimator
        return super.getChangePayload(oldItemPosition, newItemPosition);
    }
}
```
一旦实现了`DiffUtil.Callback`，可以更新`RecyclerViewAdapter`中的列表变化，代码如下：

```java
public class CustomRecyclerViewAdapter extends RecyclerView.Adapter<CustomRecyclerViewAdapter.ViewHolder> {

  ...
       public void updateEmployeeListItems(List<Employee> employees) {
        final EmployeeDiffCallback diffCallback = new EmployeeDiffCallback(this.mEmployees, employees);
        final DiffUtil.DiffResult diffResult = DiffUtil.calculateDiff(diffCallback);

        this.mEmployees.clear();
        this.mEmployees.addAll(employees);
        diffResult.dispatchUpdatesTo(this);
    }
}
```

调用`dispatctUpdatesTo(RecyclerView.Adapter)`来分配更新的列表。从diff计算返回的`DiffResult`对象，将更改分配到适配器，适配器将通知变化。

从DiffResult分配的在`getChangePayload()`返回的对象使用`notifyItemRangeChanged(position, count, payload)`，它会调用适配器的`onBindViewHolder(...List<Object> payload)`方法。

```java
@Override
public void onBindViewHolder(ProductViewHolder holder, int position, List<Object> payloads) {
// Handle the payload
}
```
`DiffUtil`还是用`RecyclerView.Adapter`方法通知适配器更新数据集：

* notifyItemMoved()
* notifyItemRangeChanged()
* notifyItemRangeInserted()
* notifyItemRangeRemoved()

可以从[这里](https://developer.android.com/reference/android/support/v7/widget/RecyclerView.Adapter.html)读到关于`RecyclerView.Adapter`的更多细节。

#### 重要：
如果列表很大，则此操作可能需要很长时间，因此建议您在后台线程上运行该命令，获取`DiffUtil#DiffResult`，然后将其应用于主线程上的`RecyclerView`。由于实现约束，列表的最大大小也可以是2<sup>26</sup>。

### 性能
`DiffUtil`需要**O(N)**空间来找出两个列表中的最小添加删除操作数。它期望的操作是**O(N + D<sup>2</sup>)**，N是添加删除对象的总数，D是编辑脚本的长度。可以查看[Android官方页面](https://developer.android.com/reference/android/support/v7/util/DiffUtil.html)获取更多性能数据。

可以从[GitHub](https://github.com/AnkitSinhal/DiffUtilExample)获取上面`DiffUtil`例子的参考实现。

感谢阅读。