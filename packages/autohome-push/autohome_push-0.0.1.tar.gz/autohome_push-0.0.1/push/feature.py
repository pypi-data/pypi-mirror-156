# coding:utf-8
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
from pyspark.sql import SparkSession, HiveContext
from pyspark.sql.types import *
import pyspark.sql.functions as F
import traceback

ConstantIntDefault = -9999999
ConstantStringDefault = '-9999999'
ConstantList1 = ['cms_series_ids', 'car_brand_ids', 'app_os_list', 'user_value1_list', 'user_value2_list',
                 'operator_list', 'user_viewcar_seri_list', 'user_viewcar_brand_list', 'user_viewcar_level_list',
                 'user_viewcar_manu_list', 'user_viewcar_manuattr_list', 'user_viewcar_country_list',
                 'user_viewcar_energy_list', 'hour_list', 'uniq_interest_brand', 'uniq_interest_seri',
                 'will_seri_list', 'often_province_list', 'often_city_list']
ConstantList2 = ['first_content_category_tag_name_uniq', 'second_content_category_tag_name_uniq',
                 'nlp_sentiment_name_uniq', 'uniq_keywords_name', 'nlp_energy_name_uniq', 'fetr_car_level_name',
                 'fetr_series_place', 'fetr_sect_name', 'fetr_spec_structure_seat', 'fetr_fuel_type',
                 'fetr_spec_transmission_type', 'fetr_spec_structure_type', 'fetr_price_range',
                 'cms_series_names']
ConstantInt = ['user_life_cycle', 'rich_level', 'user_vbu_stage', 'user_viewcar_usedcar', 'user_viewcar_video',
               'user_viewcar_smallvideo', 'user_viewcar_traveller', 'user_viewcar_newenergy',
               'user_newcar_intention', 'feed_duration_group', 'user_buycar_intention', 'user_retention',
               'user_is_register', 'user_is_vip', 'city_level', 'city_district', 'user_rfm_group',
               'user_hascar_union']
ConstantString = ['resource_id', 'device_id']
ConstantInto = ['object_class_id', 'object_line_id', 'is_quarter_active', 'is_month_active', 'is_week_active',
                'is_day_active']


def common_udf(dtype, length, default, itype):
	import sys
	reload(sys)
	sys.setdefaultencoding('utf-8')
	
	def _func(x):
		import sys
		reload(sys)
		sys.setdefaultencoding('utf-8')
		
		origin = x
		if x is None:
			if itype == 'list':
				return [default] * length
			else:
				return default
		try:
			SPLIT = ':' if ':' in x else ','
			x = str(x.decode('utf-8')).strip()
			if x == '':
				if itype == 'list':
					return [default] * length
				else:
					return default
			if itype == 'list':
				x = [t.split(SPLIT)[0] for t in x.split(';')][0:3]
			else:
				if itype == 'into' or itype == 'int':
					x = [x]
				else:
					x = [x.split(SPLIT)[0]]
			
			if dtype == 'string':
				x = map(str, x)
				x = [i.decode('utf-8') for i in x]
			else:
				x = map(int, x)
			
			if length > 1:
				x = x + [default] * (length - len(x))
			
			if itype == 'list':
				return x
			else:
				return x[0]
		except:
			sys.stderr.write('check udf error:')
			traceback.print_exc(None, file=sys.stderr)
			if itype == 'list':
				return [default] * length
			else:
				return default
	
	return _func


string_list_udf = F.udf(common_udf('string', 3, ConstantStringDefault, 'list'),
                        returnType=ArrayType(StringType()))
int_list_udf = F.udf(common_udf('int', 3, ConstantIntDefault, 'list'), returnType=ArrayType(IntegerType()))
int_single_udf = F.udf(common_udf('int', 1, ConstantStringDefault, 'single'), returnType=IntegerType())
string_single_udf = F.udf(common_udf('string', 1, ConstantStringDefault, 'single'), returnType=StringType())
into_single_udf = F.udf(common_udf('into', 1, ConstantIntDefault, 'single'), returnType=IntegerType())


def transform(df):
	"""
	transform the data into form that dnn model need
	Args:
		df:  dataframe(spark)
	"""
	column_set = set(df.columns)
	
	udfs = []
	for columns, itype, dtype in [(ConstantList1, 'list', 'int'), (ConstantList2, 'list', 'string'),
	                              (ConstantInt, 'single', 'int'), (ConstantString, 'single', 'string'),
	                              (ConstantInto, 'single', 'into')]:
		if itype == 'list':
			if dtype == 'int':
				udfs += [int_list_udf(column).alias(column) for column in columns if column in column_set]
			elif dtype == 'string':
				udfs += [string_list_udf(column).alias(column) for column in columns if column in column_set]
		else:
			if dtype == 'int':
				udfs += [int_single_udf(column).alias(column) for column in columns if column in column_set]
			elif dtype == 'string':
				udfs += [string_single_udf(column).alias(column) for column in columns if column in column_set]
			elif dtype == 'into':
				udfs += [into_single_udf(column).alias(column) for column in columns if column in column_set]
	
	df = df.select(*udfs)
	return df
