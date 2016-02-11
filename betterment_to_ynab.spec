# -*- mode: python -*-
a = Analysis(['betterment_to_ynab.py'],
             pathex=['C:\\Users\\Josh\\Dropbox\\Life_Stuff\\Finances\\Accounts\\Betterment'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None,
             excludes=['matplotlib','IPython','_ssl','_tkinter','bz2','PIL',
                       'pyexpat','PyQt4','PySide','scipy.fftpack',
                        'scipy.integrate','scipy.interpolate','scipy.io.matlab',
                        'scipy.ndimage','scipy.optimize','scipy.signal',
                         'scipy.sparse','scipy.spatial','scipy.stats',
                        'shiboken','sip','sphinx','statsmodels','tcl','tk',
                        'unicodedata','scipy.linalg'])
for d in a.datas:
    if 'pyconfig' in d[0]: 
        a.datas.remove(d)
        break
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='betterment_to_ynab.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True , icon='betterment_to_ynab.ico')
