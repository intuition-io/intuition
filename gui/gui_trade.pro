CONFIG += qt debug 
SOURCES += gui_trade.cpp WindowMain.cpp Interface.cpp
HEADERS += WindowMain.h Interface.h
TARGET = 

!exists( gui_trade.cpp ) {
    error( "No gui_trade.cpp file found. Stopping..." )
}
