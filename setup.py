from setuptools import find_packages, setup

setup(name='naviance_admissions_calculator_web',
      version='0.0.1',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      #py_modules=['naviance_admissions_calculator_web'],
      install_requires = [
          'naviance_admissions_calculator @ git+https://github.com/francaellerman/naviance_admissions_calculator',
          'flask']
      )
