#include "DataSubsystem.h"

#include <Poco/File.h>
#include <Poco/Data/SQLite/Connector.h>
#include <Poco/Util/Application.h>

#include <iostream>
#include <cassert>
#include <algorithm>
#include <iterator>

using namespace std;
using namespace Poco::Data;
using Poco::FastMutex;
using Poco::RWLock;


namespace quantrade {

DataSubsystem::DataSubsystem() :
    _pPool(0),
    _logger(Poco::Logger::get("Poco::Logger::ROOT"))
{
    std::cout << "Hello from datasubsystem constructor !\n";
    SQLite::Connector::registerConnector();
}

DataSubsystem::~DataSubsystem()
{
    SQLite::Connector::unregisterConnector();
}

const char* DataSubsystem::name() const
{
    return "DataSubsystem";
}

void DataSubsystem::connect(const std::string& dbFilename)
{
    _poolLock.lock();
    if (_pPool)
        delete _pPool;
    _logger.debug("Trying to connect to " + dbFilename);
    std::cout << "Trying to connect to " + dbFilename << std::endl;
    _pPool = new Poco::Data::SessionPool("SQLite", dbFilename);
    _poolLock.unlock();
    _dbFilename = dbFilename;
    setup();
}

void DataSubsystem::disconnect()
{
    FastMutex::ScopedLock lock(_poolLock);
    if (_pPool) {
        delete _pPool;
        _pPool = 0;
    }
}

void DataSubsystem::initialize(Poco::Util::Application& app)
{
    string dbFilename = app.config().getString("mod.database.file", "quanTrade.db");
    _logger.debug("Initiating database subsystem, connecting to database.");
    std::cout << "Initiating database subsystem, connecting to database.\n";
    connect(dbFilename);
}

void DataSubsystem::uninitialize()
{
    std::cout << "Disconnecting from database\n";
    disconnect();
}

void DataSubsystem::destroy()
{
    assert(!_pPool);
    Poco::File(_dbFilename).remove();
}

void DataSubsystem::setup()
{
    RWLock::ScopedLock lock(_dbLock, true);

    _logger.debug("Creating tables and indices, if neccessary.");
    Session session = getSession();
    session.begin();
    session <<
        "CREATE TABLE IF NOT EXISTS process ("
        "  process_id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"
        "  process_name   TEXT NOT NULL,"
        "  input_file     TEXT NOT NULL,"
        "  start_time     INTEGER NOT NULL,"
        "  sample_freq    INTEGER NOT NULL"
        ")",
        now;

    session.commit();
    _logger.debug("Data setup successful.");
}

void DataSubsystem::test() {
    string name;
    _logger.debug("Test control of the database.");
    Session session = getSession();
    session << "SELECT ticker FROM stocks WHERE id LIKE 2", into(name), now;
    std::cout << "Asset with id 2: " << name << std::endl;
}

} // namespace quantrade
