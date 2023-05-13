import re
from dan import self
from dan.cxx import Library, Executable
from dan.smc import TarSources
from dan.testing import Test, Case

version = self.options.add('version', '1.11.0').value
description = 'Fast C++ logging library'


class SpdlogSources(TarSources):
    name = 'spdlog-source'
    url = f'https://github.com/gabime/spdlog/archive/refs/tags/v{version}.tar.gz'


class Spdlog(Library):
    name = 'spdlog'
    preload_dependencies = SpdlogSources,
    dependencies = 'fmt = 9',
    public_compile_definitions = 'SPDLOG_COMPILED_LIB', 'SPDLOG_FMT_EXTERNAL'
    header_match = r'^(?:(?!bundled).)*\.(h.?)$'
    installed = True
    
    async def __initialize__(self):
        spdlog_root = self.get_dependency(SpdlogSources).output / f'spdlog-{version}'
        self.includes.add(spdlog_root  / 'include', public=True)
        spdlog_src = spdlog_root / 'src'
        self.sources = [
            spdlog_src / 'async.cpp',
            spdlog_src / 'cfg.cpp',
            spdlog_src / 'color_sinks.cpp',
            spdlog_src / 'file_sinks.cpp',
            spdlog_src / 'stdout_sinks.cpp',
            spdlog_src / 'spdlog.cpp',
        ]
        
        if self.toolchain.type != 'msvc':
            self.link_libraries.add('pthread', public=True)

        await super().__initialize__()

class SpdlogTest(Test, Executable):
    name = 'spdlog-test'
    dependencies = Spdlog,
    sources = 'test.cpp',
    cases = [
        Case('default', expected_output=re.compile(r'.+\[info\] Hello world')),
        Case('custom', 'custom', expected_output=re.compile(r'.+\[info\] Hello custom')),
    ]
