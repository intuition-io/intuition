#ifndef WINDOW_MAIN
#define WINDOW_MAIN

#include <QtGui>

class WindowMain : public QWidget {
    
    Q_OBJECT

    public:
        WindowMain();

    public slots:
        void runCommand();

    private:
        QLineEdit *cmd_line;
        QLabel *infos;
        QLabel *graph;
        QGridLayout *layout_main;
};

#endif
