#include <iostream>
#include <stdlib.h>
#include <QApplication>
#include "WindowMain.cpp"

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);

    WindowMain window;
    window.show();
    return app.exec();
}

