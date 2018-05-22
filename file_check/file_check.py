from sdss import files
import fitsio

def getRuns():
    rl = files.runlist()
    runs = rl["run"]
    if runs is None:
        raise ValueError("Unable to retrieve runs. Retrieved NoneType.")
    return runs

def runInfo(run):
    rl = files.runlist()
    w, = _np.where(rl['run'] == run)
    if len(w) == 0:
        raise ValueError("Run %s not found in runList.par" % run)
    startfield = rl[w]['startfield'][0]
    endfield = rl[w]['endfield'][0]
    return startfield, endfield

def check_fits(fitspath, errors):
    os.popen("bunzip2 -qkc "+origPathName+".bz2 >"+unpackedfits)
    img = fitsio.read(unpackedfits)
    h = fitsio.read_header(unpackedfits)
    
def check_photoObj(fitspath, errors):
    header1, header2 = fitsio.read(path_to_photoOBJ, header="True")
    files.filename("photoObj", run=_run, camcol=_camcol,
                                    field=_field)

def check_files():
    runs = getRuns()
    runs = [2888, 94] ###TESTING
    errors = open("errors.txt", a)
    
    for run in runs:
        startfield, endfield = runInfo(run)
        for field in range(startfield, endfield, 1):
            for camcol in (1,2,3,4,5,6):
                for filter in ('u', 'g', 'r', 'i', 'z'):
                        origPathName = files.filename('frame', run=run,
                                                      camcol=camcol,
                                                      field=field,
                                                      filter=filter)
                        unpackPath = os.environ["FITSDMP"]
                        fname = origPathName.split("/")[-1]
                        unpackedfits = os.path.join(unpackPath, fname)
                    try:
                        check_fits(unpackedfits)
                    except:
                        errors.write(str(run)+","+str(camcol)+","+
                                     str(field)+","+str(filter)+
                                     "FITS\n")
                    finally:
                        try: os.remove(unpackedfits)
                        except: pass

                photoObjPath = files.filename("photoObj", run=run,
                                              camcol=camcol,
                                              field=field)
                try:    
                    check_photoObj(photoObjPath)
                except:
                    errors.write(str(run)+","+str(camcol)+","+
                                 str(field)+","+str(filter)+
                                 "PHOTOOBJ\n")
                    