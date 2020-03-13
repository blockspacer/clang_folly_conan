#include <cstdlib>
#include <iostream>
#include <iterator>
#include <exception>
#include <string>
#include <algorithm>
#include <chrono>
#include <cmath>
#include <memory>
#include <vector>

// __has_include is currently supported by GCC and Clang. However GCC 4.9 may have issues and
// returns 1 for 'defined( __has_include )', while '__has_include' is actually not supported:
// https://gcc.gnu.org/bugzilla/show_bug.cgi?id=63662
#if __has_include(<filesystem>)
#include <filesystem>
#else
#include <experimental/filesystem>
#endif // __has_include

#include <boost/program_options.hpp>
#include <boost/optional.hpp>
#include <boost/optional/optional_io.hpp>
#include <boost/program_options.hpp>
#include <boost/utility/in_place_factory.hpp>


#include <folly/Format.h>
#include <folly/ProducerConsumerQueue.h>

//#include <folly/io/async/ScopedEventBaseThread.h>
#include <folly/executors/CPUThreadPoolExecutor.h>
#include <folly/executors/GlobalExecutor.h>
#include <folly/Executor.h>
#include <folly/Try.h>
#include <folly/executors/Async.h>
#include <folly/executors/GlobalExecutor.h>
#include <folly/futures/Future.h>
#include <folly/futures/Promise.h>
#include <folly/String.h>
#include <folly/FileUtil.h>
#include <folly/File.h>
#include <folly/io/IOBufQueue.h>
#include <folly/Optional.h>
#include <folly/Memory.h>
#include <folly/executors/GlobalExecutor.h>
#include <folly/io/async/EventBaseManager.h>
#include <folly/init/Init.h>
#include <folly/logging/Init.h>
#include <folly/logging/xlog.h>
#include <folly/logging/RateLimiter.h>
#include <folly/init/Init.h>
#include <folly/Singleton.h>
#include <folly/logging/Init.h>
#include <folly/portability/Config.h>
#include <folly/logging/StandardLogHandler.h>
#include <folly/Conv.h>
#include <folly/logging/Init.h>
#include <folly/logging/LogConfigParser.h>
#include <folly/logging/LogFormatter.h>
#include <folly/logging/FileHandlerFactory.h>
#include <folly/logging/StreamHandlerFactory.h>
#include <folly/logging/LogHandlerFactory.h>
#include <folly/logging/LogWriter.h>
#include <folly/logging/LoggerDB.h>
#include <folly/logging/StandardLogHandler.h>
#include <folly/logging/StandardLogHandlerFactory.h>
#include <folly/logging/xlog.h>
#include <folly/FileUtil.h>
#include <folly/Random.h>
#include <folly/ScopeGuard.h>
#include <folly/hash/SpookyHashV2.h>
#include <folly/json.h>
//#include <folly/experimental/TimerFDTimeoutManager.h>
//#include <folly/experimental/STTimerFDTimeoutManager.h>
//#include <folly/experimental/STTimerFDTimeoutManager.h>
//#include <folly/experimental/TimerFDTimeoutManager.h>
#include <folly/io/async/test/UndelayedDestruction.h>
#include <folly/executors/TimedDrivableExecutor.h>
#include <folly/Conv.h>
#include <folly/portability/GFlags.h>
#include <folly/ssl/Init.h>

#include <glog/logging.h>

#if FOLLY_USE_SYMBOLIZER
#include <folly/experimental/symbolizer/SignalHandler.h> // @manual
#endif
#include <folly/portability/GFlags.h>

namespace po = boost::program_options;

static std::shared_ptr<folly::CPUThreadPoolExecutor> CPU_executor;


template<class T>
std::ostream& operator<<(std::ostream& os, const std::vector<T>& v)
{
    copy(v.begin(), v.end(), std::ostream_iterator<T>(os, " "));
    return os;
}

/*
 * An RAII object to be constructed at the beginning of main() and destructed
 * implicitly at the end of main().
 *
 * The constructor performs the same setup as folly::init(), including
 * initializing singletons managed by folly::Singleton.
 *
 * The destructor destroys all singletons managed by folly::Singleton, yielding
 * better shutdown behavior when performed at the end of main(). In particular,
 * this guarantees that all singletons managed by folly::Singleton are destroyed
 * before all Meyers singletons are destroyed.
 */
class Init {
 public:
  // Force ctor & dtor out of line for better stack traces even with LTO.
  FOLLY_NOINLINE Init(int argc, char* argv[], boost::optional<std::string> log_config, bool removeFlags = true);
  FOLLY_NOINLINE ~Init();

  Init(Init const&) = delete;
  Init(Init&&) = delete;
  Init& operator=(Init const&) = delete;
  Init& operator=(Init&&) = delete;
};

Init::Init(int argc, char* argv[],
    boost::optional<std::string> log_config, bool removeFlags) {
#if FOLLY_USE_SYMBOLIZER
  // Install the handler now, to trap errors received during startup.
  // The callbacks, if any, can be installed later
  folly::symbolizer::installFatalSignalHandler();
#elif !defined(_WIN32)
  google::InstallFailureSignalHandler();
#endif

  // Move from the registration phase to the "you can actually instantiate
  // things now" phase.
  folly::SingletonVault::singleton()->registrationComplete();

  // similar to https://github.com/facebook/folly/blob/master/folly/init/Init.cpp#L49
  // but removed ParseCommandLineFlags
  // add support fo file logging,
  // see https://github.com/facebook/folly/blob/master/folly/logging/docs/LogHandlers.md#file-handler-type
  folly::LoggerDB::get().registerHandlerFactory(
      std::make_unique<folly::FileHandlerFactory>());

  if(log_config.is_initialized()) {
    CHECK(!log_config.value().empty())
      << "invalid (empty) log configuration";
    folly::initLoggingOrDie(log_config.value());
  } else {
    /// \see https://github.com/facebook/folly/tree/master/folly/logging/docs
    folly::initLoggingOrDie(
      ".:=INFO:default:x; default=stream:stream=stderr; x=stream:stream=stderr");
  }
  auto programName = argc && argv && argc > 0 ? (argv)[0] : "unknown";
  XLOG(DBG9) << "program name is " << programName;
  google::InitGoogleLogging(programName);

#if FOLLY_USE_SYMBOLIZER
  // Don't use glog's DumpStackTraceAndExit; rely on our signal handler.
  google::InstallFailureFunction(abort);

  // Actually install the callbacks into the handler.
  folly::symbolizer::installFatalSignalCallbacks();
#endif
}

Init::~Init() {
  folly::SingletonVault::singleton()->destroyInstances();
}

int main(int argc, char* argv[])
{
    auto str = folly::format("The answers are {} and {}", 23, 42);
    std::cout << str << std::endl;
    folly::ProducerConsumerQueue<int> someQueue{100};
    /// \note no logging before Init!
    boost::optional<std::string> log_config;
    Init(argc, argv, log_config);
    return EXIT_SUCCESS;
}
