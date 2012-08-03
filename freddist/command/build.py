from distutils.command.build import build as _build


class build(_build):
    # Add i18n sub-command
    def has_i18n_files(self):
        return self.distribution.has_i18n_files()

    sub_commands = _build.sub_commands
    sub_commands.append(('build_i18n', has_i18n_files))
