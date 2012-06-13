#include "Interface.cpp"
#include "WindowMain.h"

WindowMain::WindowMain() : QWidget() {
    this->setWindowTitle("QuanTrade v0.02");
    this->setWindowIcon(QIcon("smile.png"));
    this->setWindowOpacity(0.9);
    this->setStyleSheet("QWidget { background: black }");

    cmd_line = new QLineEdit;
    cmd_line->setStyleSheet("color: white");

    infos = new QLabel("Stocks infos field");
    infos->setStyleSheet("color: white");
    infos->setFont(QFont("Comic Sans MS", 10));

    graph = new QLabel();
    graph->setPixmap(QPixmap("test.bmp"));
    graph->setCursor(Qt::CrossCursor);

    layout_main = new QGridLayout;
    layout_main->addWidget(cmd_line, 0, 0, 8, 1);   //ligne, colonne
    layout_main->addWidget(infos, 1, 0, 8, 5);
    layout_main->addWidget(graph, 0, 9, 8, 6);

    this->setLayout(layout_main);

    QObject::connect(cmd_line, SIGNAL(returnPressed()), this, SLOT(runCommand()));
}

void WindowMain::runCommand() {
    string cmd = cmd_line->text().toStdString();
    //infos->setText(cmd_line->text());
    cmd_line->clear();
    Interface interpreter;
    interpreter.cmd_parser(cmd);
    interpreter.config_file_generator();
    system("./downloader/downloader.py -o dl -p 10");
    QString quote_infos = interpreter.infos_printer();
    infos->setText(quote_infos);
}
