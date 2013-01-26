#ifndef Backtester_H
#define Backtester_H

#include <Poco/Util/Subsystem.h>
#include <Poco/File.h>

namespace quantrade {

/**
 * Provides functions for storing objects in a SQLite database.
 */
class Backtester : public Poco::Util::Subsystem
{
public:
    /**
     * Default constructor. 
     */
    Backtester();

    /**
     * Destroys the Backtester. 
     */
    virtual ~Backtester();

    /**
     * run the node.js server, listening to clients.
     */
    void online();

    /**
     * Send a terminate signal to node.js server process.
     */
    void shutdown();

    int runLocalModule(std::string moduleName, std::vector<std::string> args);

    void test();

    /**
     * Returns the name of this subsystem.
     */
    virtual const char* name() const;

protected:
    /**
     * Initialization of the backtester subsystem.
     */
    virtual void initialize(Poco::Util::Application& app);

    /**
     * Uninitialization of the backtester subsystem.
     */
    virtual void uninitialize();


private:
    std::string     _server_script;
    std::string     _bin;
    Poco::Logger&         _logger;
};


} // quantrade namespace

#endif // Backtester_H
