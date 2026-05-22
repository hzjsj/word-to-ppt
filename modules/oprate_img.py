import re,os
from PIL import Image
import numpy as np

#额外的处理，读取不到的
def extra(binary_content):
  symbol_mapping = {
      br"\r\n":b"",#删除换行
      b"\xaa\xa4":b"\xaa\xa4\r\n", #换行符，换段符
      b"\xaa\xa5":b"\xaa\xa5\r\n",
      b",":b"\xa3\xac", #替换英文逗号
      b";":b"\xa3\xbb",#替换英文分号
  }
  for k,v in symbol_mapping.items():
      binary_content=re.sub(k,v,binary_content)
  return binary_content

class FBD_Q():#处理fbd文件问题的
    def __init__(self,fbdfile):
        self.fbdfile=fbdfile
        self.flag=False #是否是特殊处理
        self.processed_pic={}
        (self.filename,_)=os.path.splitext(self.fbdfile)
    def recover(self):
          if os.path.exists(self.filename+'_备份.fbd'):
            os.remove(self.fbdfile)
            os.rename(self.filename+'_备份.fbd',self.fbdfile)
            
    def oprate(self,choice='无色'):
      def convert_tif_to_white(input_path):
          if os.path.exists(input_path):
            try:
              image ,self.flag= Image.open(input_path),False
              dpi = image.info.get('dpi', (300, 300))# 获取原始图像的分辨率
              if image.mode == 'CMYK':# 检查图像是否为 CMYK 模式
                cmyk_array = np.array(image)  # 将图像转换为 numpy 数组
                c, m, y, k = cmyk_array[:, :, 0], cmyk_array[:, :, 1], cmyk_array[:, :, 2], cmyk_array[:, :, 3]# 分离 CMYK 通道
                # 找到青色点（C 通道值高，M 和 Y 通道值低）
                k_mask = k > 10
                if np.count_nonzero(k_mask)>0: #有黑色点
                  if color[0]:
                    cyan_mask = c > 50
                    if np.count_nonzero(cyan_mask)>0:
                      self.flag = True
                      # 将青色点转换为白色
                      cmyk_array[cyan_mask] = [0, 0, 0, 0]
                  elif color[1]:
                    magenta_mask = m > 50
                    if np.count_nonzero(magenta_mask)>0:
                      self.flag = True
                      cmyk_array[magenta_mask] = [0, 0, 0, 0]

                  if self.flag:
                    new_image = Image.fromarray(cmyk_array, mode='CMYK') # 将 numpy 数组转换回图像
                    file_name, file_extension = os.path.splitext(input_path)
                    output_path = file_name + '_processed' + file_extension
                    new_image.save(output_path, dpi=dpi)

              return self.flag
            except:
                return False
          else:
            return False
               
      def convert_eps_to_white(input_path):
        def eps1(matched):#处理答案图 cdr4
          
          c, m, k = [matched.group(name).decode('utf-8') for name in ('value1', 'value2', 'value3')]
          if c!="0.00" and color[0]: #有青色，青色是答案
            self.flag=True
            return  b'[ 1.00 0.00 %s 0.00 %s null ] set_'%(m.encode(),k.encode())
          elif m != "0.00" and color[1]: #有洋红，洋红是答案
            self.flag=True
            return  b'[ 1.00 %s 0.00 0.00 %s null ] set_'%(c.encode(),k.encode())
          else:
            return  b'[ 1.00 %s %s 0.00 %s null ] set_'%(c.encode(),m.encode(),k.encode())
        def eps2(matched):#处理新版eps
          c, m, k = [matched.group(name).decode('utf-8') for name in ('value1', 'value2', 'value3')]
          if c!="0.0000" and color[0]: #有青色，青色是答案
            self.flag=True
            return  b'0.0000 %s 0.0000 %s  create_cmyk_color set'%(m.encode(),k.encode())
          elif m != "0.0000" and color[1]: #有洋红，洋红是答案
            self.flag=True
            return  b'%s 0.0000 0.0000 %s  create_cmyk_color set'%(c.encode(),k.encode())
          else:
            return  b'%s %s 0.0000 %s  create_cmyk_color set'%(c.encode(),m.encode(),k.encode())
        def eps3(matched):#处理新版eps
          c, m, k = [matched.group(name).decode('utf-8') for name in ('value1', 'value2', 'value3')]
          if c!="0" and color[0]: #有青色，青色是答案
            self.flag=True
            return  b'0 %s 0 %s cmyk'%(m.encode(),k.encode())
          elif m != "0" and color[1]: #有洋红，洋红是答案
            self.flag=True
            return  b'%s 0 0 %s cmyk'%(c.encode(),k.encode())
          else:
            return  b'%s %s 0 %s cmyk'%(c.encode(),m.encode(),k.encode())

        if os.path.exists(input_path):
          binary_content,self.flag=open(input_path, 'rb').read(),False
          binary_content=re.sub(br'\[ 1.00 (?P<value1>\d.\d\d) (?P<value2>\d.\d\d) 0.00 (?P<value3>\d.\d\d) null \] set_', lambda matched: eps1(matched), binary_content)
          binary_content=re.sub(br'(?P<value1>\d\.\d{4}) (?P<value2>\d\.\d{4}) 0.0000 (?P<value3>\d\.\d{4})  create_cmyk_color set', lambda matched: eps2(matched), binary_content)
          binary_content=re.sub(br'(?P<value1>\d) (?P<value2>\d) 0 (?P<value3>\d) cmyk', lambda matched: eps3(matched), binary_content)

          if self.flag:
            file_name, file_extension = os.path.splitext(input_path)
            output_path = file_name + '_processed' + file_extension
            open(output_path, 'wb').write(binary_content)
          return self.flag
        else:
           return False
      #对二进制数据进行正则替换
      def pics(matched):#处理答案图
          value1,value2=[matched.group(name).decode('GB2312') for name in ('value1', 'value2')]
          def split_string_once(input_string):
            pattern = r'(?=[；，])'
            parts = re.split(pattern, input_string, maxsplit=1)
            if len(parts) == 1:
                parts.append("")
            return parts

          picname,suffix = split_string_once(value2)
          #如果不能判断扩展名，则去文件夹下查找
          picfile=os.path.join(os.path.dirname(self.fbdfile),picname)
          if not picname.lower().endswith((".eps",".tif")):
              if os.path.exists(picfile+".eps"):
                  picname,picfile=picname+".eps",picfile+".eps"
              elif os.path.exists(picfile+".tif"):
                  picname, picfile=picname+".tif",picfile+".tif"

          if color:
            if picname not in self.processed_pic:#没处理过就先出来再加进去
              print(picname)
              if picname.lower().endswith(".tif"):
                result=convert_tif_to_white(picfile)
              elif picname.lower().endswith(".eps"):
                result=convert_eps_to_white(picfile)
              else:
                result=False
              self.processed_pic[picname]=result
            else: 
              result=self.processed_pic[picname]
            file_name, file_extension = os.path.splitext(picname)
            
          else:
            result=False

          if result:#需要处理的
            if picname.lower().endswith(".tif"):
              return f'〖{value1}{file_name}_processed.tif{suffix}〗〖{value1}{file_name}.tif{suffix}〗'.encode('gb2312')
            elif picname.lower().endswith(".eps"):
              return f'〖{value1}{file_name}_processed.eps{suffix}〗〖{value1}{file_name}.eps{suffix}〗'.encode('gb2312')
          else:
            return f'〖{value1}{picname}{suffix}〗'.encode('gb2312')
      color={"青色":[1,0,0,0],"洋红":[0,1,0,0],"无色":False}[choice]#处理答案的颜色
      fbd=FBD_O(self.fbdfile)
      fbd.process_fbd()
      binary_content=extra(fbd.binary_content) #通用处理
      binary_content = re.sub(b'\xa1\xbc(?P<value1>XC|PS|TP)(?P<value2>.*?)\xa1\xbd', lambda matched:pics(matched), binary_content)
      open(self.fbdfile, 'wb').write(binary_content)

class FBD_O():#处理fbd文件的
  def __init__(self,fbdfile):
    self.fbdfile=fbdfile
    self.binary_content=open(self.fbdfile,'rb').read()
    (self.filename,_)=os.path.splitext(self.fbdfile)
    if not os.path.exists(self.filename+'_备份.fbd'):
      open(self.filename+'_备份.fbd', 'wb',).write(self.binary_content)
  def process_fbd(self,reference="modules/fbd2word_通用.fbd"):
    #按照换行切分获取每行数据
    for pair in open(reference,'rb').read().split(b'\r\n'):
      self.binary_content = re.sub(pair.split(b'\t')[0], pair.split(b'\t')[1], self.binary_content)

  def save(self):
    open(self.fbdfile, 'wb').write(self.binary_content)