<script setup lang="ts" xmlns="http://www.w3.org/1999/html">
import http from "@/router/axios";
import ProgressBar from "@/components/utils/ProgressBar.vue";
import {defineEmits, onMounted, ref, watch} from "vue";
import {ElTable, ElTableColumn, ElMessage, ElMessageBox} from "element-plus";
import type {Action} from 'element-plus'

interface wxinfo {
  pid: string;
  version: string;
  account: string;
  mobile: string;
  name: string;
  mail: string;
  wxid: string;
  filePath: string;
  key: string;
}

const percentage = ref(0);
const startORstop = ref(-1);  // 用于进度条的开始和停止 0表示0% 1表示100%

const init_type = ref("");

const is_init = ref(false);
const wxinfoData = ref<wxinfo[]>([]);

const oneWx = ref("");
const decryping = ref(false);
const isErrorShow = ref(false);
const isUseKey = ref("false");

const merge_path = ref("");
const wx_path = ref("");
const key = ref("");
const my_wxid = ref("");


const emits = defineEmits(['isAutoShow']); // 用于父组件监听子组件的事件


// 查看有多少个微信正在登录 ， 并调用init_key解密初始化
const get_wxinfo = async () => {
  try {
    wxinfoData.value = await http.post('/api/wxinfo');
    if (wxinfoData.value.length === 1) {
      selectWx(wxinfoData.value[0]);
      oneWx.value = " (检测到只有一个微信，将在5秒后自动选择) ";
      setTimeout(okWx, 5000);
    }
  } catch (error) {
    console.error('Error fetching data:', error);
    return [];
  }
}

const selectWx = async (row: wxinfo) => {
  merge_path.value = "";
  wx_path.value = row.filePath;
  key.value = row.key;
  my_wxid.value = row.wxid;
}

const okWx = () => {
  if (wx_path.value === '' && key.value === '' && my_wxid.value === '') {
    console.log("请填写完整信息! ")
    return;
  }
  if (decryping.value) {
    console.log("正在解密...，请稍后再试！")
    return;
  }
  init_key();
}

// END 查看有多少个微信正在登录 ， 并调用init_key解密初始化

const init_key = async () => {
  if (decryping.value) {
    console.log("正在解密中，请稍后再试！")
    return;
  }
  decryping.value = true;
  try {
    decryping.value = true;
    startORstop.value = 0; // 进度条开始
    let reqdata = {
      "wx_path": wx_path.value,
      "key": key.value,
      "my_wxid": my_wxid.value
    }
    const body_data = await http.post('/api/init_key', reqdata);
    is_init.value = body_data.is_init;
    if (body_data.is_init) {
      percentage.value = 100; // 进度条 100%
    }
    decryping.value = false;
    emits('isAutoShow', body_data.is_init);
  } catch (error) {
    percentage.value = 0; // 进度条 0%
    isErrorShow.value = true;
    decryping.value = false;
    ElMessageBox.alert(error, 'error', {
      confirmButtonText: '确认',
      callback: (action: Action) => {
        ElMessage({
          type: 'error',
          message: `action: ${action}`,
        })
      },
    })
    return [];
  }
  decryping.value = false;
}

const init_nokey = async () => {
  try {
    let reqdata = {
      "wx_path": wx_path.value,
      "merge_path": merge_path.value,
      "my_wxid": my_wxid.value
    }
    const body_data = await http.post('/api/init_nokey', reqdata);
    is_init.value = body_data.is_init;
    if (body_data.is_init) {
      percentage.value = 100; // 进度条 100%
    }
    decryping.value = false;
    emits('isAutoShow', body_data.is_init);
  } catch (error) {
    percentage.value = 0; // 进度条 0%
    isErrorShow.value = true;
    decryping.value = false;
    ElMessageBox.alert(error, 'error', {
      confirmButtonText: '确认',
      callback: (action: Action) => {
        init_type.value = "";// 刷新
      },
    })
    // console.error('Error fetching data:', error);
    return [];
  }
  decryping.value = false;
}

const init_last = async () => {
  try {
    let reqdata = {
      "wx_path": wx_path.value,
      "merge_path": merge_path.value,
      "my_wxid": my_wxid.value
    }
    const body_data = await http.post('/api/init_last', reqdata);
    is_init.value = body_data.is_init;
    if (body_data.is_init) {
      percentage.value = 100; // 进度条 100%
      decryping.value = false;
      emits('isAutoShow', body_data.is_init);
    } else {
      isErrorShow.value = true;
      decryping.value = false;
      ElMessageBox.alert("未发现上次的设置数据！", 'error', {
        confirmButtonText: '确认',
        callback: (action: Action) => {
          init_type.value = "";// 刷新
        },
      })
    }

    decryping.value = false;
  } catch (error) {
    // percentage.value = 0; // 进度条 0%
    isErrorShow.value = true;
    decryping.value = false;
    ElMessageBox.alert(error, 'error', {
      confirmButtonText: '确认',
      callback: (action: Action) => {
        init_type.value = "";
      },
    })
    // console.error('Error fetching data:', error);
    return [];
  }

  decryping.value = false;
}

// 监测isAutoShow是否为aoto，如果是则执行get_wxinfo
watch(init_type, (val) => {
  if (val === 'auto') {
    get_wxinfo();
  } else if (val === 'custom') {
    // init();
  } else if (val === 'last') {
    init_last();
  }
})

</script>

<template>
  <div style="background-color: #d2d2fa; height: 100vh; display: flex; justify-content: center; align-items: center;">
    <!-- 自动解密和显示 -->
    <div v-if="init_type==='auto'">

      <!--      <el-progress v-if="decryping && !isErrorShow" type="dashboard" :percentage="percentage" :color="colors"/>-->
      <div v-if="decryping">
        <ProgressBar v-if="decryping" :startORstop="startORstop"/>
      </div>
      <div v-else
           style="background-color: #fff; width: 90%;min-width: 800px; height: 80%; border-radius: 10px; padding: 20px; overflow: auto;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div style="font-size: 20px; font-weight: bold;">选择要查看的微信</div>
        </div>
        <div style="margin-top: 20px;">
          <el-table :data="wxinfoData" @current-change="selectWx" highlight-current-row style="width: 100%">
            <el-table-column :min-width="30" prop="pid" label="进程id"></el-table-column>
            <el-table-column :min-width="40" prop="version" label="微信版本"></el-table-column>
            <el-table-column :min-width="40" prop="account" label="账号"></el-table-column>
            <el-table-column :min-width="40" prop="name" label="昵称"></el-table-column>
            <el-table-column :min-width="50" prop="wxid" label="微信原始id"></el-table-column>
          </el-table>
        </div>
        <div style="margin-top: 20px;">
          <el-button style="margin-right: 10px;margin-top: 10px;width: 100%;" type="success" @click="okWx">确定{{
              oneWx
            }}
          </el-button>
        </div>
      </div>
    </div>
    <!-- END -->

    <!-- 用于自定义参数 -->
    <div v-else-if="init_type==='custom'">
      <div v-if="decryping">
        <ProgressBar v-if="decryping" :startORstop="startORstop"/>
      </div>
      <div v-else
           style="background-color: #fff; width: 80%;min-width: 800px; height: 70%; border-radius: 10px; padding: 20px; overflow: auto;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div style="font-size: 20px; font-weight: bold;">自定义-文件位置</div>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <!--          <el-button style="margin-right: 10px;" @click="exportData">导出</el-button>-->
          </div>
        </div>
        <div style="margin-top: 20px;">
          <!--    单选按钮      -->
          <input type="radio" v-model="isUseKey" value="true"/> 使用 KEY &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
          <input type="radio" v-model="isUseKey" value="false"/> 不使用 KEY
          <div v-if="isUseKey=='false'">
            说明：1、表示数据库已解密并合并<br>2、合并后的数据库需要包含(MediaMSG,MSG,MicroMsg,OpenIMMsg)这些数据库合并的内容<br>
          </div>
          <div v-if="isUseKey=='true'">
            说明：1、自动根据key解密微信文件夹下的数据库<br>2、必须保证key正确，否则解密失败<br>
          </div>

          <el-divider></el-divider>  <!-- 分割线-->

          <div v-if="isUseKey=='true'">
            <label>密钥key(必填): </label>
            <el-input placeholder="密钥key (64位)" v-model="key" style="width: 80%;"></el-input>
            <br>
          </div>
          <div v-if="isUseKey=='false'">
            <label>merge_all.db 文件路径(必填,非文件夹): </label>
            <el-input placeholder="(MediaMSG.db,MSG.db,MicroMsg.db,OpenIMMsg.db)合并后的数据库" v-model="merge_path"
                      style="width: 80%;"></el-input>
            <br>
          </div>
          <label>微信文件夹路径(必填): </label>
          <el-input placeholder="C:\***\WeChat Files\wxid_*******" v-model="wx_path" style="width: 80%;"></el-input>
          <br>
          <label>微信原始id(必填): </label>
          <el-input placeholder="wxid_*******" v-model="my_wxid" style="width: 80%;"></el-input>
          <br>

          <el-button v-if="isUseKey=='true'" style="margin-top: 10px;width: 100%;" type="success" @click="init_key">
            确定
          </el-button>
          <el-button v-if="isUseKey=='false'" style="margin-top: 10px;width: 100%;" type="success" @click="init_nokey">
            确定
          </el-button>
        </div>
      </div>
    </div>
    <!-- END -->

    <!-- 上次数据 -->
    <div v-else-if="init_type==='last'"></div>
    <!-- END -->

    <!-- 初始选择界面 -->
    <div v-else-if="init_type === ''" style="display: flex; justify-content: space-between;">
      <label
          style="width: 200px; height: 150px; background-color: #fff; display: flex; flex-direction: column; align-items: center; border-radius: 10px; margin-right: 20px;">
        <input type="radio" v-model="init_type" value="last"/>
        <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%;">
          <div>使用上次设置</div>
        </div>
      </label>
      <label
          style="width: 200px; height: 150px; background-color: #fff; display: flex; flex-direction: column; align-items: center; border-radius: 10px; margin-right: 20px;">
        <input type="radio" v-model="init_type" value="auto"/>
        <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%;">
          <div>自动解密已登录微信</div>
        </div>
      </label>
      <label
          style="width: 200px; height: 150px; background-color: #fff; display: flex; flex-direction: column; align-items: center; border-radius: 10px;">
        <input type="radio" v-model="init_type" value="custom"/>
        <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%;">
          <div>自定义文件位置</div>
        </div>
      </label>
    </div>
    <!-- END -->
  </div>
</template>

<style scoped>

</style>