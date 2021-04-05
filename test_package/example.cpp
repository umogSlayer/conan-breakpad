#ifdef __APPLE__ 
#include "client/mac/handler/exception_handler.h"

static bool dumpCallback(const char* _dump_dir, const char* _minidump_id, void* context, bool success) {
  printf("Dump path: %s\n", _dump_dir);
  return success;
}
#endif

#ifdef _WIN32
#include "client/windows/handler/exception_handler.h"

bool dumpCallback(const wchar_t* _dump_dir,
                  const wchar_t* _minidump_id,
                  void* context,
                  EXCEPTION_POINTERS* exinfo,
                  MDRawAssertionInfo* assertion,
                  bool success) {
  wprintf(L"Dump path: %s\n", _dump_dir);
  return true;
}
#endif

#ifdef __linux__
#include <breakpad/client/linux/handler/exception_handler.h>
#include <breakpad/client/linux/handler/minidump_descriptor.h>
static bool dumpCallback(
    const google_breakpad::MinidumpDescriptor &md,
    void *context,
    bool succeeded)
{
    return false;
}
#endif

int main(int argc, char* argv[]) {
#ifdef __APPLE__
  std::string path = "/tmp";
  google_breakpad::ExceptionHandler eh(path, NULL, dumpCallback, NULL, true, NULL);
#endif

#ifdef _WIN32
  std::wstring path = L"C:\\tmp";
  google_breakpad::ExceptionHandler eh(path, 0, dumpCallback, 0, google_breakpad::ExceptionHandler::HandlerType::HANDLER_ALL);
#endif

#ifdef __linux__
  using google_breakpad::MinidumpDescriptor;
  using google_breakpad::ExceptionHandler;
  MinidumpDescriptor md("/tmp");
  ExceptionHandler eh(md, nullptr, static_cast<ExceptionHandler::MinidumpCallback>(dumpCallback), nullptr, true, -1);
#endif

  return 0;
}
