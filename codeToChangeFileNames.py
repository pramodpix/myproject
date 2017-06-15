import os
def changeFileName(filepath):
        directory=os.path.abspath(filepath)
        number=0
        C_name='Img' #Change according to your requirement
        ext='jpg' #Change according to your requirement
        for file_name in os.listdir(directory):
                print (file_name)                
                new_file_number = number + 1
 
                new_file_name = '%s/%s%d.%s' % (directory,C_name, new_file_number,ext)
                old_file_name = '%s/%s' % (directory, file_name)
 
                os.rename(old_file_name, new_file_name)
                number+=1
 
