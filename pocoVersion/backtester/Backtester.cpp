#include "Backtester.h"

using namespace std;

namespace quantrade {

Backtester::Backtester() : _logger(quantrade::TradeLogger::get("Backtester")) 
{}

Backtester::~Backtester() {}

const char* Backtester::name() const
{
    return "Trading Backtester, powered py quantopian engine: zipline";
}

//TODO: Distributed modules
int Backtester::runLocalModule(string moduleName, vector<string> args) {
    int rc(0);
    _logger.information("Runnig backtester server: " + moduleName + " " + args[0]);
    try
    {
        Poco::Pipe outPipe;
        Poco::ProcessHandle ph = Poco::Process::launch(moduleName, args, 0, &outPipe, 0);
        Poco::PipeInputStream istr(outPipe);
        Poco::StreamCopier::copyStream(istr, std::cout);
        rc = ph.wait();
    }
    catch (Poco::SystemException& exc)
    {
        _logger.warning(exc.displayText());
    }
    return rc;
}

void Backtester::online()
{
    _logger.information("Running node server online.");
    vector<string> args;
    args.push_back(_server_script);
    int rc = runLocalModule(_bin, args);
    if ( rc != 0 )
    {
        _logger.error("** Forking " + _bin + " " + _server_script + " failed: " + toStr(rc));
    }
}

void Backtester::initialize(Poco::Util::Application& app)
{
    //TODO Get env variable here and add it  
    _logger.information("Initiating backtester subsystem, turning server node online.");
    _server_script = app.config().getString("mod.server.script", "server.js");
    _bin = app.config().getString("mod.server.bin", "nodejs");
}

void Backtester::uninitialize()
{
    _logger.information("Disconnecting from backtester network...\n");
    shutdown();
}

void Backtester::shutdown()
{
    //TODO stop here backtester thread
}

void Backtester::test() {
    _logger.debug("Test control of the backtester.");
}

} // namespace quantrade
