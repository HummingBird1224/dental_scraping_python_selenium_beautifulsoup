from bs4 import BeautifulSoup
import requests
import csv
from normalize_japanese_addresses import normalize

base_url='https://www.ibaraki-medinfo.jp/details/'

f = open("urls.txt", "r")

data=['storename', 'address_original', 'address_normalize[0]', 'address_normalize[1]', '最終更新日', 'url', 
      '開設者種別', '開設者名', '管理者名', '歯科一般領域一覧', '歯科口腔外科領域一覧', '小児歯科領域一覧', '矯正歯科領域一覧',
      '施設状況一覧', '対応可能ﾅ麻酔治療一覧', '在宅医療', '連携ﾉ有無', '歯科医師(総数|常勤|非常勤)', '歯科技工士(総数|常勤|非常勤)', 
      '歯科助手(総数|常勤|非常勤)', '歯科衛生士(総数|常勤|非常勤)', '前年度1日平均外来患者数', '緯度', '経度', 'page']

fc=open('ibaraki.csv', 'a', newline='',encoding='utf-8')
# Create a CSV writer object
writer = csv.writer(fc)
# Write the data to the CSV file
writer.writerow(data)

def get_page(id, category):
  response = requests.get(base_url+category+'/sb/'+id)
  return response

def get_base_data(html):
  soup = BeautifulSoup(html, 'lxml')
  span_items = soup.find("h3", {"class": "kikanMidashi"}).findAll("span")
  baseData={
    'storename': span_items[0].text.replace('\u3000', ' '),
    'updated_at': span_items[1].text.split('更新日：')[1].split('\n')[0],
  }
  table_items=soup.findAll("table", {"class", "input_info"})
  baseData['address']=table_items[3].findAll('tr')[2].find('td').text.replace('\u3000', ' ')
  try:
     storeAddressNormalize = "".join(list(normalize(baseData['address']).values())[0:4])
     baseData['address_normalize_1'] = _split_buildingName(storeAddressNormalize)[0]
     baseData['address_normalize_2'] = _split_buildingName(storeAddressNormalize)[1]
  except:
     baseData['address_normalize_1']=baseData['address_normalize_2']="na"
  baseData['founder_type']=table_items[1].find('tr').find('td').text.replace('\u3000', ' ')
  baseData['founder_name']=table_items[1].findAll('tr')[2].find('td').text.replace('\u3000', ' ')
  baseData['admin_name']=table_items[2].findAll('tr')[1].find('td').text.replace('\u3000', ' ')
  return baseData

def get_amenity_data(html):
  soup = BeautifulSoup(html, 'lxml')
  true_elements=soup.findAll('td', string='有')
  
  if len(true_elements) > 0 :
    amenityData=[]
    for t_el in true_elements :
      parent_true=t_el.find_parent('tr')
      amenityData.append(parent_true.find('th').text.strip())
  else :
    amenityData='na'
  
  return amenityData

def get_actual_data(html):
  soup = BeautifulSoup(html, 'lxml')
  table_items=soup.findAll("table", {"class", "input_info"})
  dentist_element=table_items[0].find('div', string='歯科医師')
  actualData={}
  if not dentist_element is None:
    parent_dentist=dentist_element.find_parent('tr')
    den_total=parent_dentist.findAll('td')[1].find('div').text if parent_dentist.findAll('td')[1].find('div').text!='' else '-'
    den_full=parent_dentist.findAll('td')[2].find('div').text if parent_dentist.findAll('td')[2].find('div').text!='' else '-'
    den_part=parent_dentist.findAll('td')[3].find('div').text if parent_dentist.findAll('td')[3].find('div').text!='' else '-'
    actualData['dentist']=den_total+'|'+ den_full + '|' + den_part
  else:
    actualData['dentist']='na'

  hygienist_element=table_items[0].find('div', string='歯科衛生士')
  if not hygienist_element is None:
    parent_hygienist=hygienist_element.find_parent('tr')
    hyg_total=parent_hygienist.findAll('td')[1].find('div').text if parent_hygienist.findAll('td')[1].find('div').text!='' else '-'
    hyg_full=parent_hygienist.findAll('td')[2].find('div').text if parent_hygienist.findAll('td')[2].find('div').text!='' else '-'
    hyg_part=parent_hygienist.findAll('td')[3].find('div').text if parent_hygienist.findAll('td')[3].find('div').text!='' else '-'
    actualData['dental_hygienist']= hyg_total+'|'+ hyg_full + '|' + hyg_part
  else:
    actualData['dental_hygienist']='na'

  day_element=table_items[len(table_items)-1].find('div', string='前年度１日平均患者数')
  actualData['day_patients']='na'
  if not day_element is None:
    parent_day=day_element.find_parent('tr')
    actualData['day_patients']=parent_day.findAll('td')[1].find('div').text.split('人')[0] if parent_day.findAll('td')[1].find('div').text!='' else 'na'

  return actualData

def get_contents_data(html):
  soup = BeautifulSoup(html, 'lxml')
  contentsData={}

  general_div=soup.find("span", string="歯科領域").find_parent('div')
  general_element=general_div.find_next_sibling('table').findAll('tr')
  if len(general_element) > 1:
    general_dentistry=[]
    for g_el in general_element[1:]:
      general_dentistry.append(g_el.find('td').text)
  else :
    general_dentistry='na'
  contentsData['general_dentistry']=general_dentistry

  oral_div=soup.find("span", string="口腔外科領域").find_parent('div')
  oral_element=oral_div.find_next_sibling('table').findAll('tr')
  if len(oral_element) > 1:
    oral_surgery=[]
    for o_el in oral_element[1:]:
      oral_surgery.append(o_el.find('td').text)
  else :
    oral_surgery='na'
  contentsData['oral_surgery']=oral_surgery

  homecare_div=soup.find("span", string="対応することができる在宅医療（在宅医療）").find_parent('div')
  homecare_element=homecare_div.find_next_sibling('table').findAll('tr')
  if len(homecare_element) > 1:
    homecare=[]
    for h_el in homecare_element:
      homecare.append(h_el.find('td').text)
  else :
    homecare='na'      
  contentsData['homecare']=homecare

  collaboration_div=soup.find("span", string="対応することができる在宅医療（他施設との連携）").find_parent('div')
  collaboration_element=collaboration_div.find_next_sibling('table').findAll('tr')
  if len(collaboration_element) > 1:
    collaboration=[]
    for c_el in collaboration_element:
      collaboration.append(c_el.find('td').text)
  else :
    collaboration='na'   
  contentsData['collaboration']=collaboration

  return contentsData


for line in f :
  page=line.split(',')[0]
  id=line.split(',')[1]
  data={}
  baseInfo=get_page(id, 'BaseInfo')
  if baseInfo.status_code == 200:
    baseData=get_base_data(baseInfo.text)

  amenityInfo=get_page(id, 'Amenity')
  if amenityInfo.status_code == 200:
    amenityData=get_amenity_data(amenityInfo.text)

  actualInfo=get_page(id, 'Actual')
  if actualInfo.status_code == 200:
    actualData=get_actual_data(actualInfo.text)

  contentsInfo=get_page(id, 'Contents')
  if contentsInfo.status_code == 200:
    contentsData=get_contents_data(contentsInfo.text)

  data=[
    baseData['storename'],
    baseData['address'],
    baseData['address_normalize_1'],
    baseData['address_normalize_2'],
    baseData['updated_at'],
    base_url+'BaseInfo'+'/sb/'+id,
    baseData['founder_type'],
    baseData['founder_name'],
    baseData['admin_name'],
    contentsData['general_dentistry'],
    contentsData['oral_surgery'],
    'na',
    'na',
    amenityData,
    'na',
    contentsData['homecare'],
    contentsData['collaboration'],
    actualData['dentist'],
    'na',
    'na',
    actualData['dental_hygienist'],
    actualData['day_patients'],
    'na',
    'na',
    page
  ]
  writer.writerow(data)
  print(id)

fc.close()
