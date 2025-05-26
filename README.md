PS C:\Users\anurag\Desktop\AnomSched> cd .\build\
PS C:\Users\anurag\Desktop\AnomSched\build> cmake -G "MinGW Makefiles" ..
-- The C compiler identification is GNU 14.2.0
-- The CXX compiler identification is GNU 14.2.0
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Check for working C compiler: C:/msys64/ucrt64/bin/cc.exe - skipped
-- Detecting C compile features
-- Detecting C compile features - done
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Check for working CXX compiler: C:/msys64/ucrt64/bin/c++.exe - skipped
-- Detecting CXX compile features
-- Detecting CXX compile features - done
-- Configuring done (2.7s)
-- Generating done (0.0s)
-- Build files have been written to: C:/Users/anurag/Desktop/AnomSched/build
PS C:\Users\anurag\Desktop\AnomSched\build> mingw32-make
[ 25%] Building CXX object CMakeFiles/AnomSched.dir/src/main.cpp.obj
[ 50%] Building CXX object CMakeFiles/AnomSched.dir/src/scheduler.cpp.obj
[ 75%] Building CXX object CMakeFiles/AnomSched.dir/src/logger.cpp.obj
[100%] Linking CXX executable AnomSched.exe
[100%] Built target AnomSched
PS C:\Users\anurag\Desktop\AnomSched\build> ./AnomSched.exe               
Starting scheduler with intentional anomalies...
ANOMALY: Job 3 sleeping for 336ms
ANOMALY: Job 28 sleeping for 574ms
ANOMALY: Job 48 sleeping for 419ms
ANOMALY: Job 47 sleeping for 495ms
ANOMALY: Job 16 sleeping for 729ms
ANOMALY: Job 6 sleeping for 704ms
ANOMALY: Job 46 sleeping for 459ms
ANOMALY: Job 76 sleeping for 646ms
ANOMALY: Job 36 sleeping for 611ms
ANOMALY: Job 34 sleeping for 672ms
ANOMALY: Job 94 sleeping for 800ms
ANOMALY: Job 31 sleeping for 740ms
ANOMALY: Job 11 sleeping for 499ms
ANOMALY: Job 61 sleeping for 680ms
ANOMALY: Job 80 sleeping for 570ms
Scheduler stopped.
PS C:\Users\anurag\Desktop\AnomSched\build> 