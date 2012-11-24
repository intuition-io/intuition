#ifndef DATASUBSYSTEM_H
#define DATASUBSYSTEM_H

#include <Poco/Logger.h>
#include <Poco/Mutex.h>
#include <Poco/RWLock.h>
//#include <Poco/Data/Common.h>
//#include "Poco/Data/Session.h"
#include <Poco/Data/SessionPool.h>
#include <Poco/Util/Subsystem.h>


namespace quantrade {

/**
 * Provides functions for storing objects in a SQLite database.
 */
class DataSubsystem : public Poco::Util::Subsystem
{
public:
    /**
     * Default constructor. Registers the SQLite connector.
     */
    DataSubsystem();

    /**
     * Destroys the DataSubsystem. Unregisters the SQLite connector.
     */
    virtual ~DataSubsystem();

    /**
     * Attaches the given database file.
     */
    void connect(const std::string& dbFilename);

    /**
     * Detaches the current database file.
     */
    void disconnect();

    /**
     * Detaches the current database file and deletes it.
     */
    void destroy();

    void test();

    /**
     * Returns the name of this subsystem.
     */
    virtual const char* name() const;

protected:
    /**
     * Initialization of the database subsystem.
     */
    virtual void initialize(Poco::Util::Application& app);

    /**
     * Uninitialization of the database subsystem.
     */
    virtual void uninitialize();

    /**
     * Further setup of the database subsystem, i.e. ensure all
     * tables/relations exist.
     */
    void setup();

    /**
     * Returns a Session object from the SessionPool.
     */
    inline Poco::Data::Session getSession();

    Poco::RWLock _dbLock;


private:
    std::string              _dbFilename;
    Poco::Data::SessionPool* _pPool;
    Poco::FastMutex          _poolLock;
    Poco::Logger&            _logger;
};

inline Poco::Data::Session DataSubsystem::getSession()
{
    Poco::FastMutex::ScopedLock lock(_poolLock);
    poco_check_ptr(_pPool);
    return _pPool->get();
}

} // quantrade namespace

#endif // DATASUBSYSTEM_H
