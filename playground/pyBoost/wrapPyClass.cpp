#include <iostream>
#include <string>

#include <boost/python.hpp>
#include <Python.h>

//using namespace boost::python;
namespace py = boost::python;

void greet()
{ 
  // Retrieve the main module.
    py::object main = py::import("__main__");
  
  // Retrieve the main module's namespace
    py::object global(main.attr("__dict__"));

  // Define greet function in Python.
    //py::object result = py::exec(
    //"def greet():                   \n"
    //"   return 'Hello from Python!' \n",
    //global, global);
    py::object result = py::exec_file("classTest.py", global, global);

  // Create a reference to it.
    py::object greet = global["Test"];

  // Call it.
  std::string message = py::extract<std::string>(greet());
  std::cout << message << std::endl;
}

int main() {
    Py_Initialize();
    greet();
    return 0;
}
