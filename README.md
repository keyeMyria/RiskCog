# RiskCog 

## 多人合作
1. 克隆仓库到本地
```
git clone https://github.com/cyruscyliu/diffentropy.git
git remote -v
```
2. 创建develop分支
```
git checkout -b develop origin/develop
```
3. 关联develop分支
```
git branch --set-upstream develop origin/develop
```
4. 在develop中创建自己的分支
```
git checkout -b yourname
```
5. 推送 
```
git add *
git commit -m 'description'
git checkout develop
git merge yourname
# push first time
git push -u origin develop
# push later
git push origin develop
```
6. 如发生冲突
```
git pull
```
7. 在本地解决冲突
+ 查看冲突文件
```
git status
```
+ 直接打开文件进行编辑
+ 重新添加/提交/推送

## 分支操作
+ 创建并切换到分支
```
git checkout -b yourbranchname

# 等价于以下两条命令
git branch yourbranchname
git checkout yourbranchname
```
+ 查看分支
```
git branch
```
+ 切换回master
```
git checkout master
```
+ 合并新分支到master(必须先切换到master分支)
```
# ff
git merge yourbranchname
# no-ff(recommend)
git merge --no-ff -m 'merge with no-ff' yourbranchname
```
+ 删除分支
```
git branch -d yourbranchname
```
6. 解决冲突
+ 合并冲突后查看冲突文件
```
git status
```
+ 直接打开文件进行选择
+ 重新添加/提交
+ 合并即完成
+ 删除分支(可选)
7. BUG分支
```
# assume current branch is cyrus, the bug is in master
git stash
git status # display clean
git checkout master
git checkout -b issue-001
... # fix the bug
git checkout master
git merge -no-ff -m '...' issue-001
git checkout cyrus
git stash pop
```
