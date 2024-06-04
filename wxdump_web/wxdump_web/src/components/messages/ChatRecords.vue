<script setup lang="ts">
import ChatRecprdsHeader from '@/components/messages/ChatRecprdsHeader.vue';
import ChatRecordsMain from '@/components/messages/ChatRecordsMain.vue';
import {ref, defineProps, nextTick, onMounted, watch} from 'vue';
import http from "@/router/axios.js";
import ChatExportMain from "@/components/chatBackup/ChatExportMain.vue";

// start 关于滚动条的操作

const scrollbarRef = ref(null);
const chatRecordsMainRef = ref(null);
const scrollTop = ref(0);
const scrollHeight = ref(0);

const scrollToBottom = () => {
  nextTick(() => {
    if (scrollbarRef.value) {
      // 假设el-scrollbar在DOM中是一个具体的元素
      const target = scrollbarRef.value.$el.children[0];
      if (target) {
        target.scrollTop = target.scrollHeight;
        scrollHeight.value = target.scrollHeight;
      }
    }
  });
};

const updateScrollTop = () => {
  const target = scrollbarRef.value.$el.children[0];
  if (target) {
    const lastScrollHeight = scrollHeight.value;
    const heightDiff = target.scrollHeight - lastScrollHeight;
    target.scrollTop = target.scrollTop + heightDiff;
    scrollHeight.value = target.scrollHeight;
  }
}

function handleScroll({scrollTop}) {
  if (scrollTop === 0) {
    if (chatRecordsMainRef.value) {
      chatRecordsMainRef.value.loadMore()
    }
  }
}

// end 关于滚动条的操作


interface User {
  wxid: string
  nickname: string
  remark: string
  account: string
  describe: string
  headImgUrl: string
  msg_count: number
}

const props = defineProps({
  wxid: {
    type: String,
    required: true,
  }
});

const userinfo = ref<User>({
  account: '',
  describe: '',
  headImgUrl: '',
  nickname: '',
  remark: '',
  wxid: '',
  msg_count: 0,
});

// 请求数据 用户信息
const req_user_info = async () => {
  try {
    const body_data = await http.post('/api/wxid2user', {
      'wxid': props.wxid,
    });
    userinfo.value.account = body_data[props.wxid].account;
    userinfo.value.describe = body_data[props.wxid].describe;
    userinfo.value.headImgUrl = body_data[props.wxid].headImgUrl;
    userinfo.value.nickname = body_data[props.wxid].nickname;
    userinfo.value.remark = body_data[props.wxid].remark;
    userinfo.value.wxid = props.wxid;
    return body_data;
  } catch (error) {
    console.error('Error fetching data wxid2user :', error);
    return [];
  }
}

// 请求数据 聊天记录数量
const req_msg_count = async () => {
  try {
    const body_data = await http.post('/api/msg_count', {
      'wxid': props.wxid,
    });
    // body:{wxid_k330vxwt2mjx12: 26}
    userinfo.value.msg_count = body_data[props.wxid];
    return body_data;
  } catch (error) {
    console.error('Error fetching data msg_count:', error);
    return [];
  }
}
// 调用函数请求数据与聊天记录数量
onMounted(() => {
  req_msg_count();
  req_user_info();
//   等待数据加载完成后，再滚动到底部
  nextTick(() => {
    scrollToBottom();
  });
});

// 导出聊天记录页面是否显示
const is_export = ref(false);
const onExport = (exporting: boolean) => {
  is_export.value = exporting;
  if (is_export.value === false) {
    // 修改wxid后，重新请求数据
    userinfo.value.wxid = '';
    req_user_info();
  }

}
// end 导出聊天记录页面是否显示

// start 监测wxid变化
watch(() => props.wxid, async (newVal, oldVal) => {
  if (newVal !== oldVal) {
    req_user_info();
    req_msg_count();
    is_export.value = false;
    nextTick(() => {
      scrollToBottom();
    });
  }
});


</script>

<template>
  <el-container>
    <el-header style="height: 65px; max-height: 65px; width: 100%;background-color: #d2d2fa;padding-top: 5px;">
      <ChatRecprdsHeader :userData="userinfo" @exporting="onExport"/>
    </el-header>

    <el-main style="overflow-y: auto; height: calc(100vh - 65px);padding: 0">
      <el-scrollbar ref="scrollbarRef" @scroll="handleScroll">

        <ChatExportMain v-if="is_export" :wxid="userinfo.wxid"/>
        <ChatRecordsMain v-else
                         ref="chatRecordsMainRef"
                         :userData="userinfo"
                         :setScrollTop="scrollToBottom"
                         :updateScrollTop="updateScrollTop"
        />
      </el-scrollbar>
    </el-main>
  </el-container>
</template>

<style scoped>

</style>
