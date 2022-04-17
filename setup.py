from distutils.core import setup
setup(name='naviance_admissions_calculator_web',
      version='1.0',
      py_modules=['naviance_admissions_calculator_web'],
      install_requires = [
          'naviance_admissions_calculator @ git+https://github.com/francaellerman/naviance_admissions_calculator@v1.1#egg=naviance_admissions_calculator',]
      )
