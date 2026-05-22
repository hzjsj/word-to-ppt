import fitz
import os
#返回pdf页面的信息
def get_info(doc_path):
  pdf_path =doc_path.replace(".docx", ".pdf") 
  if not os.path.exists(pdf_path): #如果没有pdf，用wps生成
    # windows下输出pdf
    from win32com.client import DispatchEx
    import pythoncom
    pythoncom.CoInitialize()
    word_app=DispatchEx("KWPS.Application")
    word_app.Visible , word_app.ScreenUpdating = True,True
    doc = word_app.Documents.Open(doc_path)
  
    doc.ExportAsFixedFormat(OutputFileName= pdf_path, ExportFormat=17)
    doc.Close()
    word_app.Quit()
    pythoncom.CoUninitialize()


  #ubuntu利用上传的pdf
  # 获取pdf页面信息 
  pdf_document = fitz.open(pdf_path)
  informations={}#构建页面信息结构
  for num in range(0,pdf_document.page_count):
    informations[num]={"tables":[],"imgs":[],"contents":[] }
    page = pdf_document.load_page(num)
    #获取文字段落信息
    infos,breaks=[],[]
    for a in page.get_texttrace():
        for b in a['chars']:
            infos.append((b[0],b[3]))
    for i in range(len(infos)):
      if infos[i][0]==94 :#找到了一个段落
        breaks.append(i)
    breaks.append(i+1)

    for i in range(len(breaks)-1): #合并文字段落
      left=min([a[1][0] for a in infos[breaks[i]:breaks[i+1]]])
      top=min([a[1][1] for a in infos[breaks[i]:breaks[i+1]]])
      right=max([a[1][2] for a in infos[breaks[i]:breaks[i+1]]])
      bottom=max([a[1][3] for a in infos[breaks[i]:breaks[i+1]]])
      indent=infos[breaks[i]][1][0]-27.95  #常量
      width,height = right-left,bottom-top
      informations[num]["contents"].append((left,top,width,height,indent))
    

    for data in page.get_text("dict")['blocks']:
      if data['type']==1:
        informations[num]["imgs"].append((data['bbox'][0],data['bbox'][1],data['bbox'][2]-data['bbox'][0],data['bbox'][3]-data['bbox'][1],data['image']))
    #查找表格的旧方法
    # tabs = page.find_tables()  
    # for i,tab in enumerate(tabs): 
    #     row_position=[]
    #     for i in range(1,len(tab.rows)):
    #         row_position.append(tab.rows[i].bbox[1]-tab.rows[i-1].bbox[1])
    #     row_position.append(tab.rows[-1].bbox[3]-tab.rows[-1].bbox[1])
    #     informations[num]["tables"].append((tab.bbox[0],tab.bbox[1],tab.bbox[2],tab.bbox[3],row_position))

    for a in  page.get_cdrawings():
      if a["type"]=="s":
        if a['color']==(0.6000000238418579, 0.20000000298023224, 0.0): #表格的开始
            left,top,width=a['rect'][0],a['rect'][1],a['rect'][2]-a['rect'][0]
            hposition=a['rect'][1]
            informations[num]["tables"].append([left,top,width,0,[]])
        elif a['color']==(0.0, 0.0, 1.0):
            if informations[num]["tables"]:
              informations[num]["tables"][-1][4].append(a['rect'][1]-hposition)
              hposition=a['rect'][1]

  pdf_document.close()  

  return informations

'''# pdf尺寸
# page_width, page_height = page.mediabox.width, page.mediabox.height
# left_maragin ,right_maragin ,top_maragin ,bottom_maragin = 12.5,12.5,15,15
# 获取字体，修改成字体映射，包含黑白体，正斜体
font_names = dict()
for page_num in range(pdf_document.page_count):
    page = pdf_document.load_page(page_num)
    for a in page.get_fonts():
        font_names[a[3]]=[]
'''