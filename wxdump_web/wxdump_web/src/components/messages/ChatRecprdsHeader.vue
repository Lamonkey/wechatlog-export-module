<script setup lang="ts">
import {defineEmits, defineProps, ref} from 'vue';
import http from "@/router/axios.js";
import {ElTable, ElNotification, ElMessage, ElMessageBox} from "element-plus";

interface User {
  account: string
  describe: string
  headImgUrl: string
  nickname: string
  remark: string
  wxid: string
  msg_count: number
}

const props = defineProps({
  userData: {
    type: Object as () => User,
    required: true,
  }
});

const getting_real_time_msg = ref(false);

const get_real_time_msg = async () => {
  if (getting_real_time_msg.value) {
    console.log("正在获取实时消息，请稍后再试!")
    return;
  }
  getting_real_time_msg.value = true;
  try {
    const body_data = await http.post('/api/realtimemsg', {});
    getting_real_time_msg.value = false;

    // 滚动消息提醒
    ElNotification({
      title: 'Success',
      message: '获取实时消息成功!',
      type: 'success',
    })

    return body_data;
  } catch (error) {
    getting_real_time_msg.value = false;
    ElNotification({
      title: 'Error',
      message: '获取实时消息失败!',
      type: 'error',
    })
    console.error('Error fetching data:', error);
    return [];
  }
}

const is_export = ref(false);

const emits = defineEmits(['exporting']);
const export_button = () => {
// 提交参数 is_export 给父组件
  emits('exporting', true);
  is_export.value = true;
}

const chatview_button = () => {
// 提交参数 is_export 给父组件
  emits('exporting', false);
  is_export.value = false;
}

</script>

<template>

  <el-row :gutter="5" style="width: 100%;">
    <el-col :span="6" style="white-space: nowrap;">
      <el-text class="label_color mx-1" truncated>wxid:</el-text>&ensp;
      <el-text class="data_color mx-1" truncated :title="userData.wxid">{{ userData.wxid }}</el-text>
    </el-col>
    <el-col :span="6" style="white-space: nowrap;">
      <el-text class="label_color mx-1" truncated>账号:</el-text>&ensp;
      <el-text class="data_color mx-1" truncated :title="userData.account">{{ userData.account }}</el-text>
    </el-col>
    <el-col :span="6" style="white-space: nowrap;">
      <el-text class="label_color mx-1" truncated>昵称:</el-text>&ensp;
      <el-text class="data_color mx-1" truncated :title="userData.nickname">{{ userData.nickname }}</el-text>
    </el-col>
    <el-col :span="6" style="white-space: nowrap;">
      <el-text class="label_color mx-1" truncated>备注:</el-text>&ensp;
      <el-text class="data_color mx-1" truncated :title="userData.remark">{{ userData.remark }}</el-text>
    </el-col>
  </el-row>

  <el-row :gutter="5" style="width: 100%;">
    <el-col :span="3" style="white-space: nowrap;">
      <el-text class="label_color mx-1" truncated>数量:</el-text>&ensp;
      <el-text class="data_color mx-1" truncated :title="userData.msg_count">{{ userData.msg_count }}</el-text>
    </el-col>
    <el-col :span="15" style="white-space: nowrap;">
      <el-text class="label_color mx-1" truncated>描述:</el-text>&ensp;
      <el-text class="data_color mx-1" truncated :title="userData.describe">{{ userData.describe }}</el-text>
    </el-col>
    <el-col :span="3" style="white-space: nowrap;">
      <el-text class="button_color mx-1 underline" truncated @click="get_real_time_msg();">实时消息
        <template v-if="getting_real_time_msg" style="color: #00bd7e">(获取中)</template>
      </el-text>
    </el-col>
    <el-col :span="3" style="white-space: nowrap;">
      <el-text v-if="!is_export" class="button_color mx-1 underline" truncated @click="export_button();">导出备份</el-text>
      <el-text v-if="is_export" class="button_color mx-1 underline" truncated @click="chatview_button();">聊天查看</el-text>
    </el-col>
  </el-row>

</template>

<style scoped>
.label_color {
  color: #333; /* 调整字体颜色 */
  font-size: 15px;
  padding-left: 15px;
  padding-right: 0;
}


.data_color {
  color: #08488c;
  background-color: #f4f4f4; /* 调整背景颜色 */
  font-size: 15px;
  padding-left: 6px;
  padding-right: 6px;
  font-weight: bold; /* 使用 bold 表示加粗 */
  white-space: nowrap;
  max-width: 80%;
}

.button_color {
  color: #0048ff; /* 调整字体颜色 */
  font-size: 15px;
  padding-left: 15px;
  padding-right: 0;
  text-decoration: underline;
}

</style>