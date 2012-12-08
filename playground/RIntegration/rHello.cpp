#include <RInside.h>                    // for the embedded R via RInside

int main(int argc, char *argv[]) {

    RInside R(argc, argv);              // create an embedded R instance

    //R["txt"] = "Hello, world!\n";	// assign a char* (string) to 'txt'
    //R.parseEvalQ("cat(txt)");           // eval the init string, ignoring any returns
    
    std::string txt = "Hello, world !\n";
    R.assign(txt, "txt");
    std::string evalstr = "cat(txt)";
    R.parseEval(evalstr);

    exit(0);
}
