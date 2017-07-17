import os
import jinja2
import codecs

INDICES = {
	'date': 0,
	'receiver': 1,
	'address': 2,
	'city': 3,
	'cost_id': 4,
	'bill_no': 5,
	'start_items': 6
}

heads = list(['amount','unit','text','price_per_unit','price'])

MAX_LINES = 20 #max lines per page


def render(tpl_path, context):
	path, filename = os.path.split(tpl_path)
	return jinja2.Environment(
					loader=jinja2.FileSystemLoader(path or './')
	).get_template(filename).render(context)

def read_source(src):
	data = None
	with codecs.open(src, "r", "utf-8") as file:
					data = list(file)

	context = {}
	context['date'] = data[INDICES['date']]
	context['receiver'] = data[INDICES['receiver']]
	context['address'] = data[INDICES['address']]
	context['city'] = data[INDICES['city']]
	context['cost_id'] = data[INDICES['cost_id']]
	context['bill_no'] = data[INDICES['bill_no']]


	start = INDICES['start_items']

	ids = list()

	page_ids = list()
	page_ids.append(start)


	data_len = len(data) - 1


	prove_comm = None
	for d in data[start:]:
		if d.startswith('#'):
			prove_comm = True
			break


	if prove_comm:
		i = start
		while i<data_len:
			if i//MAX_LINES >= len(page_ids):

				if not data[i].startswith('#'):
					page_ids.append(ids[-1])
					i = ids[-1]-1
				else:
					page_ids.append(i)

			if data[i].startswith('#'):
				if i not in ids:
					ids.append(i)

			i += 1
			print('i:',i)
	else:
		for i,d in enumerate(data[start:]):
			if i//MAX_LINES >= len(page_ids):
				page_ids.append(i)


	ids.append(len(data)-start-1)

	pages_list = list()
	page_sum_before = 0.0
	for i,id in enumerate(page_ids):
		next_id = page_ids[i+1] if (i+1)<len(page_ids) else data_len
		page = {}
		items = list()
		page_sum = 0.0

		for d in data[id:next_id]:
			if d.startswith('#'):
				items.append({'name': d[1:].rstrip()})
			else:
				items.append({ h: v.rstrip() for (h,v) in zip(heads,d.split(',')) })
				page_sum += float(d.split(',')[-1])
		page['items'] = items
		page['sum'] = page_sum

		page['first-page'] = True if i==0 else False
		page['last-page'] = True if i==len(page_ids)-1 else False
		page['sum-before'] = page_sum_before
		page_sum_before = page_sum

		pages_list.append(page)

	context['pages'] = pages_list

	discount = data[len(data)-1]

	if discount != '0':
		context['discount'] = discount

	return context,len(data)






def get_total_price(context):
	netto = 0.0
	mwst = 0.0
	brutto = 0.0

	for p in context['pages']:
		for i in p['items']:
			if not 'name' in i:
				netto += float(i['price'])

	zs = netto
	if 'discount' in context:
		zs = netto + float(context['discount'])

	mwst = zs*0.2
	brutto = zs+mwst

	if 'discount' in context:
		return ('netto',netto),('zs',zs),('mwst',mwst),('brutto',brutto)

	return ('netto',netto),('mwst',mwst),('brutto',brutto)


# price_info = get_total_price(context)
#
# for k,v in price_info:
# 	context[k] = v
#
# result = render('template.html', context)

scontext,lines = read_source('source.txt')
print(scontext)
price_info = get_total_price(scontext)
for k,v in price_info:
	scontext[k] = v

result = render('template.html', scontext)

with open("bill.html", "w") as f:
	f.write(result)

import pdfkit
options = {
    'page-size': 'A4',
    'encoding': "UTF-8",
	'dpi': 400,
	'header-right':'[page]/[toPage]'
}
pdfkit.from_url('file:///Users/Moerti/AA_projects/bill-creator/bill.html', 'out.pdf', options=options)


### so soll context aussehen
# context = {
# 	'pages':[
# 		{'items':
# 				[
# 				{'name': 'Kommission 1'},
# 				{'amount':5, 'unit': 'lfm', 'text': 'Store nähen', 'price_per_unit': 10, 'price': -50},
# 				{'amount':5, 'unit': 'lfm', 'text': 'FB', 'price_per_unit': 1, 'price': 5},
# 				{'amount':5,'unit':'lfm','text':'ziehen','price_per_unit':2,'price':10},
# 				{'name': 'Kommission 2'},
# 				{'amount': 5, 'unit': 'lfm', 'text': 'Store naehen', 'price_per_unit': 10, 'price': 50},
# 				{'amount': 5, 'unit': 'lfm', 'text': 'FB', 'price_per_unit': 1, 'price': 5},
# 				{'amount': 5, 'unit': 'lfm', 'text': 'ziehen', 'price_per_unit': 2, 'price': 10},
# 				{'name': 'Kommission 3'},
# 				{'amount': 5, 'unit': 'lfm', 'text': 'Store naehen', 'price_per_unit': 10, 'price': 50},
# 				{'amount': 5, 'unit': 'lfm', 'text': 'FB', 'price_per_unit': 1, 'price': 5},
# 				{'amount': 5, 'unit': 'lfm', 'text': 'ziehen', 'price_per_unit': 2, 'price': 10}
# 				],
# 		'sum': 122,
# 		'first-page': True,
# 		'last-page': False,
# 		'sum-before': 0
# 		},
# 		{'items':
# 			[
# 				{'name': 'Kommission 1'},
# 				{'amount': 5, 'unit': 'lfm', 'text': 'Store nähen', 'price_per_unit': 10, 'price': -50},
# 				{'amount': 5, 'unit': 'lfm', 'text': 'FB', 'price_per_unit': 1, 'price': 5},
# 				{'amount': 5, 'unit': 'lfm', 'text': 'ziehen', 'price_per_unit': 2, 'price': 10},
# 				{'name': 'Kommission 2'},
# 				{'amount': 5, 'unit': 'lfm', 'text': 'Store naehen', 'price_per_unit': 10, 'price': 50},
# 				{'amount': 5, 'unit': 'lfm', 'text': 'FB', 'price_per_unit': 1, 'price': 5},
# 				{'amount': 5, 'unit': 'lfm', 'text': 'ziehen', 'price_per_unit': 2, 'price': 10},
# 				{'name': 'Kommission 3'},
# 				{'amount': 5, 'unit': 'lfm', 'text': 'Store naehen', 'price_per_unit': 10, 'price': 50},
# 				{'amount': 5, 'unit': 'lfm', 'text': 'FB', 'price_per_unit': 1, 'price': 5},
# 				{'amount': 5, 'unit': 'lfm', 'text': 'ziehen', 'price_per_unit': 2, 'price': 10}
# 			],
# 			'sum': 334,
# 			'first-page': False,
# 			'last-page': False,
# 			'sum-before': 122
# 		},
# 		{'items':
# 			[
# 				{'name': 'Kommission 1'},
# 				{'amount': 5, 'unit': 'lfm', 'text': 'Store nähen', 'price_per_unit': 10, 'price': -50},
# 				{'amount': 5, 'unit': 'lfm', 'text': 'FB', 'price_per_unit': 1, 'price': 5},
# 				{'amount': 5, 'unit': 'lfm', 'text': 'ziehen', 'price_per_unit': 2, 'price': 10},
# 				{'name': 'Kommission 2'},
# 				{'amount': 5, 'unit': 'lfm', 'text': 'Store naehen', 'price_per_unit': 10, 'price': 50},
# 				{'amount': 5, 'unit': 'lfm', 'text': 'FB', 'price_per_unit': 1, 'price': 5},
# 				{'amount': 5, 'unit': 'lfm', 'text': 'ziehen', 'price_per_unit': 2, 'price': 10},
# 				{'name': 'Kommission 3'},
# 				{'amount': 5, 'unit': 'lfm', 'text': 'Store naehen', 'price_per_unit': 10, 'price': 50},
# 				{'amount': 5, 'unit': 'lfm', 'text': 'FB', 'price_per_unit': 1, 'price': 5},
# 				{'amount': 5, 'unit': 'lfm', 'text': 'ziehen', 'price_per_unit': 2, 'price': 10}
# 			],
# 			'sum': 122,
# 			'first-page': False,
# 			'last-page': True,
# 			'sum-before': 334
# 		}
# 	],
# 	'location': 'Tragwein',
# 	'date': '15.06.2017',
# 	'receiver': 'Patrick Moertenboeck',
# 	'address': 'Gartenstrasse 12',
# 	'city': 'Tragwein',
# 	'bill_no': 'TR231',
# 	'discount': -10.15
# }
