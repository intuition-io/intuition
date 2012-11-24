#include <iostream>
#include "utils.h"
#include "TradeCenter.h"
#include "Interface.cpp"

using namespace std;


int TradeCenter::runModule(string moduleName, vector<string> args) {
  int rc(0);
  try
  {
    Poco::Pipe outPipe;
    Poco::ProcessHandle ph = Poco::Process::launch(moduleName, args, 0, &outPipe, 0);
    Poco::PipeInputStream istr(outPipe);
    Poco::StreamCopier::copyStream(istr, std::cout);
    rc = ph.wait();
    logger().information(Poco::format("return code = %d", rc));
  }
  catch (Poco::SystemException& exc)
  {
    logger().warning(exc.displayText());
  }
  return rc;
}

int TradeCenter::main(const vector<string>& args) {
#ifdef DEBUG
  logger().information("Debug mode activated");
#endif
#ifdef OS_LINUX
  logger().information("Opearting system: Linux");
#endif

  if ( !_helpRequested ) {
    logger().information("Application properties:");
    printProperties("");

    /*
     * Crée le noyau manageant la configuration requise
     */
    Interface core;

    /*
     *Lecture du fichier de configuration et paramétrage du process
     */
    if ( core.init("./config.json") < 0 )
      logger().information("** Error initializing");

    vector<string> args;
    //args.push_back("-al");
    //string prog = "ls";
    string prog = "./test/dist/testModule-x86_64";
    int rc = runModule(prog, args);
    if ( rc != 0 )
      logger().error("** Forking failed: " + toStr(rc));

    /*
     * Process module execution
     * Should loop over modules stored from config file
     */
    //if ( core.generateConfigFile("basic") < 0 )
      //logger().information("** Error generating configuration file, module");

    //if ( core.process("basic") != 0 )
      //logger().information("** Error processing module");
  }

  //TODO generateReport()
  //TODO readReport();
  //TODO Envoyer argv[1] ou des saisies d'utilisateur pour influencer le process ?
  return Application::EXIT_OK;
}
