#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <cctype>
#include <queue>
#include <algorithm>
using namespace std;

#define MAX_SIZE 100
#define MAX_TITLE 100
#define MAX_CONTENT 500
#define MAX_CATEGORY 20
#define MAX_AUTHOR 50
#define MAX_KEYWORD 50
#define MAX_DOCS_PER_KEY 50
#define DATA_FILE "documents.txt"
#define MAX_POINT 100
#define INF 0x3f3f3f3f

// 文档结构
struct Document {
    int id;
    char title[MAX_TITLE], content[MAX_CONTENT], category[MAX_CATEGORY];
    char author[MAX_AUTHOR], status[20], publishDate[20];
};

// 检索筛选条件
struct Filter {
    char category[MAX_CATEGORY], author[MAX_AUTHOR], status[20];
    char startDate[20], endDate[20];
};

// 文档顺序表管理
class DocManager {
protected:
    Document data[MAX_SIZE];
    int length;
public:
    DocManager() { length = 0; }
    int getLength() { return length; }
    Document* getDoc(int idx) { return idx >= 0 && idx < length ? &data[idx] : nullptr; }

    int findIndexById(int id) {
        for (int i = 0; i < length; i++) if (data[i].id == id) return i;
        return -1;
    }

    bool addDoc(const Document& doc) {
        if (length >= MAX_SIZE) return false;
        data[length++] = doc;
        return true;
    }

    bool deleteById(int id) {
        int pos = findIndexById(id);
        if (pos == -1) return false;
        for (int i = pos; i < length - 1; i++) data[i] = data[i+1];
        length--;
        return true;
    }

    bool updateById(int id, const char* t, const char* c, const char* ca,
                    const char* a, const char* s, const char* d) {
        int pos = findIndexById(id);
        if (pos == -1) return false;
        if (t && *t) strcpy(data[pos].title, t);
        if (c && *c) strcpy(data[pos].content, c);
        if (ca && *ca) strcpy(data[pos].category, ca);
        if (a && *a) strcpy(data[pos].author, a);
        if (s && *s) strcpy(data[pos].status, s);
        if (d && *d) strcpy(data[pos].publishDate, d);
        return true;
    }

    Document* findById(int id) {
        int pos = findIndexById(id);
        return pos == -1 ? nullptr : &data[pos];
    }

    void saveToFile() {
        FILE* fp = fopen(DATA_FILE, "w");
        if (!fp) return;
        fprintf(fp, "%d\n", length);
        for (int i = 0; i < length; i++) {
            fprintf(fp, "%d\n%s\n%s\n%s\n%s\n%s\n%s\n",
                data[i].id, data[i].title, data[i].content, data[i].category,
                data[i].author, data[i].status, data[i].publishDate);
        }
        fclose(fp);
    }

    void loadFromFile() {
        FILE* fp = fopen(DATA_FILE, "r");
        if (!fp) return;
        int n;
        fscanf(fp, "%d\n", &n);
        Document tmp;
        for (int i = 0; i < n && i < MAX_SIZE; i++) {
            fscanf(fp, "%d\n", &tmp.id);
            fgets(tmp.title, MAX_TITLE, fp); tmp.title[strcspn(tmp.title, "\n")] = 0;
            fgets(tmp.content, MAX_CONTENT, fp); tmp.content[strcspn(tmp.content, "\n")] = 0;
            fgets(tmp.category, MAX_CATEGORY, fp); tmp.category[strcspn(tmp.category, "\n")] = 0;
            fgets(tmp.author, MAX_AUTHOR, fp); tmp.author[strcspn(tmp.author, "\n")] = 0;
            fgets(tmp.status, 20, fp); tmp.status[strcspn(tmp.status, "\n")] = 0;
            fgets(tmp.publishDate, 20, fp); tmp.publishDate[strcspn(tmp.publishDate, "\n")] = 0;
            addDoc(tmp);
        }
        fclose(fp);
    }
};

// 撤销栈相关
enum OpType { OP_ADD, OP_DELETE, OP_UPDATE };
struct Action { OpType type; Document doc; };
class UndoStack {
    static const int MAX_UNDO = 20;
    Action arr[MAX_UNDO];
    int top;
public:
    UndoStack() : top(0) {}
    bool push(Action ac) { return top < MAX_UNDO ? arr[top++] = ac, true : false; }
    bool pop(Action& out) { return top ? out = arr[--top], true : false; }
    bool empty() { return top == 0; }
};

// 搜索历史循环队列
class SearchHistoryQueue {
    static const int HSIZE = 10;
    char his[HSIZE][MAX_CONTENT];
    int front, rear, cnt;
public:
    SearchHistoryQueue() : front(0), rear(0), cnt(0) {}
    void enq(const char* s) {
        strncpy(his[rear], s, MAX_CONTENT-1);
        rear = (rear + 1) % HSIZE;
        cnt == HSIZE ? front = (front+1)%HSIZE : cnt++;
    }
    void show() {
        if (!cnt) { puts("暂无搜索历史"); return; }
        int p = front;
        for (int i = 0; i < cnt; i++, p=(p+1)%HSIZE) printf("%d. %s\n", i+1, his[p]);
    }
};
