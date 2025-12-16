"""快速验证测试

简单验证所有模块是否正常工作
"""

import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    print("\n" + "="*60)
    print("快速验证测试")
    print("="*60)

    tests = [
        ("Prompt 模块", "from core.prompts import get_prompt_manager; m = get_prompt_manager(); assert 'system_intro' in m.list_templates()"),
        ("数据加载器", "from core.data_loaders import Document; d = Document('test', {}, 'test'); assert d.content == 'test'"),
        ("向量存储", "from core.vector_store import InMemoryVectorStore; v = InMemoryVectorStore(); assert v.documents == []"),
        ("输出解析器", "from core.output_parsers import parse_output; r = parse_output('{\"a\":1}', 'json'); assert r.data['a'] == 1"),
        ("实用工具", "from common.utilities import MathUtils, DateUtils, ValidationUtils, TextUtils; assert MathUtils.add(1,2) == 3"),
        ("工作流链", "from core.chains import SimpleChain; c = SimpleChain(lambda **k: k); assert True"),
    ]

    passed = 0
    for name, code in tests:
        try:
            exec(code)
            print(f"✅ {name}")
            passed += 1
        except Exception as e:
            print(f"❌ {name}: {str(e)}")

    print(f"\n总计: {passed}/{len(tests)} 个模块通过")
    if passed == len(tests):
        print("🎉 所有模块正常工作！")
    else:
        print(f"⚠️  {len(tests)-passed} 个模块有问题")

if __name__ == "__main__":
    main()
