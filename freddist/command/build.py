from distutils.command.build import build as _build


class build(_build):
    """Has two more phases - i18n compilation and SCSS compilation."""

    def has_i18n_files(self):
        return self.distribution.has_i18n_files()

    def has_scss_files(self):
        return self.distribution.has_scss_files()

    sub_commands = _build.sub_commands
    sub_commands.append(('build_i18n', has_i18n_files))
    sub_commands.append(('build_scss', has_scss_files))
