#  The MIT License (MIT)
#
#  Copyright (c) 2021. Scott Lau
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import logging

import numpy as np
import pandas as pd
from config42 import ConfigManager
from sc_analyzer_base import BranchUtils, ManifestUtils

from sc_retail_analysis.analyzer.base_analyzer import BaseAnalyzer


class DepositAnalyzer(BaseAnalyzer):
    """
    存款分析
    """

    def __init__(self, *, config: ConfigManager, excel_writer: pd.ExcelWriter):
        super().__init__(config=config, excel_writer=excel_writer)
        self._key_enabled = "retail.non_interest.deposit.enabled"
        self._key_business_type = "retail.non_interest.deposit.business_type"
        self._key_export_column_list = "retail.non_interest.deposit.sheet_config.export_column_list"

    def _read_config(self, *, config: ConfigManager):
        self._src_filepath = config.get("retail.non_interest.deposit.source_file_path")
        self._sheet_name = config.get("retail.non_interest.deposit.sheet_name")
        self._header_row = config.get("retail.non_interest.deposit.sheet_config.header_row")
        # 工号列索引
        self._id_column = self._calculate_column_index_from_config(
            config, "retail.non_interest.deposit.sheet_config.id_column"
        )
        # 姓名列索引
        self._name_column = self._calculate_column_index_from_config(
            config, "retail.non_interest.deposit.sheet_config.name_column"
        )
        # 所属机构列索引
        self._branch_column = self._calculate_column_index_from_config(
            config, "retail.non_interest.deposit.sheet_config.branch_column"
        )
        # 需要统计的列的索引与输出列名对
        key = "retail.non_interest.deposit.sheet_config.value_column_pairs"
        self._init_value_column_config(config, key)

    def _read_src_file(self) -> pd.DataFrame:
        logging.getLogger(__name__).info("读取源文件：{}".format(self._src_filepath))
        data = pd.read_excel(self._src_filepath, sheet_name=self._sheet_name, header=self._header_row, thousands=",")
        self._id_column_name = data.columns[self._id_column]
        self._name_column_name = data.columns[self._name_column]
        self._branch_column_name = data.columns[self._branch_column]
        self._init_value_column_pairs(data)
        return data

    def _add_export_column_manifest_branch(self, origin_data: pd.DataFrame):
        if origin_data is None or origin_data.empty:
            return origin_data
        # 与花名册整合，添加花名册所在部门一列
        data = origin_data.merge(
            ManifestUtils.get_name_branch_data_frame(),
            how="left",
            left_on=[self._name_column_name],
            right_on=[ManifestUtils.get_name_column_name()]
        )
        return data

    def _rename_target_columns(self, *, data: pd.DataFrame) -> pd.DataFrame:
        df = data.rename(columns=self._value_column_pairs)
        return df

    def _replace_common_account(self, *, df: pd.DataFrame, id_column_name: str, name_column_name: str,
                                branch_column_name: str):
        """
        处理公共户

        如果客户经理是公共户，则归属到对应的机构去，将客户经理名称修改为对应机构名称
        :param df: DataFrame
        :param id_column_name: ID列名称
        :param name_column_name: 姓名列名称
        :param branch_column_name: 机构列名称
        :return: 替换公共户和机构名称后的DataFrame
        """
        for row_i, row in df.iterrows():
            name = row[name_column_name]
            branch_name = row[branch_column_name]
            new_branch_name = BranchUtils.replace_branch_name(branch_name=branch_name)
            if BranchUtils.is_common_account(name):
                df.at[row_i, name_column_name] = new_branch_name
                df.at[row_i, id_column_name] = 0

    def _pre_pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        logging.getLogger(__name__).info("开始处理公共户信息...")
        self._replace_common_account(df=data, id_column_name=self._id_column_name,
                                     name_column_name=self._name_column_name,
                                     branch_column_name=self._branch_column_name)
        logging.getLogger(__name__).info("解决姓名与工号不匹配的问题...")
        # 将工号变成数字，好与匹配花名册，修正员工名称错误的问题
        data[self._id_column_name] = data[self._id_column_name].astype("int64")
        data = ManifestUtils.fix_name_error(data, self._id_column_name, self._name_column_name)
        return data

    def _pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        index_columns = [
            self._id_column_name,
            self._name_column_name,
        ]
        value_columns = self._get_value_columns()
        logging.getLogger(__name__).info("按{} 透视数据项：{}".format(
            index_columns,
            value_columns,
        ))
        if data.empty:
            return pd.DataFrame(columns=index_columns + value_columns)
        table = pd.pivot_table(data,
                               values=value_columns,
                               index=index_columns,
                               aggfunc=np.sum, fill_value=0)
        return table

    def _after_pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        data.reset_index(inplace=True)
        # 调整列的顺序
        columns_list = [
            self._id_column_name,
            self._name_column_name,
        ]
        columns_list.extend(self._value_column_pairs.values())
        data = data[columns_list]
        return data

    def _merge_with_manifest(self, *, manifest_data: pd.DataFrame, data: pd.DataFrame) -> pd.DataFrame:
        logging.getLogger(__name__).info("与花名册合并...")
        merge_result = ManifestUtils.merge_with_manifest(manifest_data=manifest_data, data=data,
                                                         id_column_name=self._id_column_name,
                                                         name_column_name=self._name_column_name)
        return merge_result

    def _drop_duplicated_columns(self, *, data: pd.DataFrame) -> pd.DataFrame:
        return data.drop(columns=[self._id_column_name, self._name_column_name])

    def _add_target_columns(self) -> None:
        self._add_value_pair_target_columns()
