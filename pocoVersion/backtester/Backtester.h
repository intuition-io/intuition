#include <Poco/Util/Application.h>
#include <Poco/Util/Option.h>
#include <Poco/Util/OptionSet.h>
#include <Poco/Util/HelpFormatter.h>
#include <Poco/Util/AbstractConfiguration.h>
#include <Poco/AutoPtr.h>
#include <Poco/Process.h>
#include <Poco/Pipe.h>
#include <Poco/PipeStream.h>
#include <Poco/StreamCopier.h>
#include <Poco/Format.h>

#include <iostream>

#include "../dataSubSystem/DataSubsystem.cpp"

using Poco::Util::Application;
using Poco::Util::Option;
using Poco::Util::OptionSet;
using Poco::Util::HelpFormatter;
using Poco::Util::AbstractConfiguration;
using Poco::Util::OptionCallback;
using Poco::AutoPtr;

class Backtester: public Application
{
public:
	Backtester(): _helpRequested(false) {
    setUnixOptions(true);
    addSubsystem(new quantrade::DataSubsystem);
  }

protected:	
	void initialize(Application& self)
	{
    loadConfiguration(); // load default configuration files, if present
    Application::initialize(self);
    logger().information("Initiating application...");
	}
	
	void uninitialize()
	{
		// add your own uninitialization code here
        logger().information("Shutting down Backtester module...");
		Application::uninitialize();
	}
	
	void reinitialize(Application& self)
	{
		Application::reinitialize(self);
		// add your own reinitialization code here
	}
	
	void defineOptions(OptionSet& options)
	{
		Application::defineOptions(options);

		options.addOption(
			Option("help", "h", "display help information on command line arguments")
				.required(false)
				.repeatable(false)
				.callback(OptionCallback<Backtester>(this, &Backtester::handleHelp)));

		options.addOption(
			Option("define", "D", "define a configuration property")
				.required(false)
				.repeatable(true)
				.argument("name=value")
				.callback(OptionCallback<Backtester>(this, &Backtester::handleDefine)));
				
		options.addOption(
			Option("config-file", "f", "load configuration data from a file")
				.required(false)
				.repeatable(true)
				.argument("file")
				.callback(OptionCallback<Backtester>(this, &Backtester::handleConfig)));

		options.addOption(
			Option("bind", "b", "bind option value to Backtester.property")
				.required(false)
				.repeatable(false)
				.argument("value")
				.binding("Backtester.property"));
	}

    /* Doesn't work */
    void handleOption(const std::string& name, const std::string& value)
    {
        Application::handleOption(name, value);
        logger().warning("Handling options");
        if (name == "num-threads")
            logger().critical("Threads requested: " + value);
        if (name == "test")
            logger().critical("Test flag");
    }

	void handleHelp(const std::string& name, const std::string& value)
	{
		_helpRequested = true;
		displayHelp();
		stopOptionsProcessing();
	}
	
	void handleDefine(const std::string& name, const std::string& value)
	{
		defineProperty(value);
	}
	
	void handleConfig(const std::string& name, const std::string& value)
	{
		loadConfiguration(value);
	}
		
	void displayHelp()
	{
		HelpFormatter helpFormatter(options());
    helpFormatter.setUnixStyle(true);
		helpFormatter.setCommand(commandName());
		helpFormatter.setUsage("OPTIONS");
		helpFormatter.setHeader("A sample application that demonstrates some of the features of the Poco::Util::Application class.");
		helpFormatter.format(std::cout);
	}
	
	void defineProperty(const std::string& def)
	{
		std::string name;
		std::string value;
		std::string::size_type pos = def.find('=');
		if (pos != std::string::npos)
		{
			name.assign(def, 0, pos);
			value.assign(def, pos + 1, def.length() - pos);
		}
		else name = def;
		config().setString(name, value);
	}

	int main(const std::vector<std::string>& args);
  int runLocalModule(std::string moduleName, std::vector<std::string> args);
	
private:
	bool _helpRequested;
};

//POCO_APP_MAIN(Backtester);

int main (int argc, char** argv) {
    Poco::AutoPtr<Backtester> pApp = new Backtester;
    try {
        pApp->init(argc, argv);
    } catch (Poco::Exception& e) {
        pApp->logger().log(e);
        return Poco::Util::Application::EXIT_CONFIG;
    }
    if ( pApp->initialized() ) {
        pApp->logger().debug("Application has been successfully initialized");
    }
    pApp->logger().debug("===========\tRunning Backtester Module\t==========\n");
    return pApp->run();
}
