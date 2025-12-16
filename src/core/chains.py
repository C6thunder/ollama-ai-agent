"""工作流链模块

提供各种工作流链功能，用于组合多个组件
支持顺序链、并行链、条件链等复杂工作流
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Union
import logging

logger = logging.getLogger(__name__)


class BaseChain(ABC):
    """工作流链基类"""

    @abstractmethod
    async def run(self, **kwargs) -> Any:
        """运行链

        Args:
            **kwargs: 输入参数

        Returns:
            输出结果
        """
        pass

    @abstractmethod
    async def batch(self, inputs: List[Dict[str, Any]]) -> List[Any]:
        """批量运行

        Args:
            inputs: 输入列表

        Returns:
            输出结果列表
        """
        pass

    def __or__(self, other: 'BaseChain') -> 'SequentialChain':
        """支持 | 操作符

        Args:
            other: 下一个链

        Returns:
            顺序链
        """
        return SequentialChain(chains=[self, other])

    def __and__(self, other: 'BaseChain') -> 'ParallelChain':
        """支持 & 操作符

        Args:
            other: 并行链

        Returns:
            并行链
        """
        return ParallelChain(chains=[self, other])


class SequentialChain(BaseChain):
    """顺序链 - 按顺序执行多个链"""

    def __init__(self, chains: List[BaseChain]):
        """初始化顺序链

        Args:
            chains: 链列表
        """
        if not chains or len(chains) < 2:
            raise ValueError("顺序链至少需要2个链")

        self.chains = chains

    async def run(self, **kwargs) -> Any:
        """顺序执行所有链

        Args:
            **kwargs: 输入参数

        Returns:
            最后链的输出
        """
        result = kwargs
        for chain in self.chains:
            logger.info(f"执行链: {chain.__class__.__name__}")
            result = await chain.run(**result)
        return result

    async def batch(self, inputs: List[Dict[str, Any]]) -> List[Any]:
        """批量顺序执行

        Args:
            inputs: 输入列表

        Returns:
            输出列表
        """
        results = []
        for input_data in inputs:
            result = await self.run(**input_data)
            results.append(result)
        return results


class ParallelChain(BaseChain):
    """并行链 - 并行执行多个链"""

    def __init__(self, chains: List[BaseChain], max_workers: Optional[int] = None):
        """初始化并行链

        Args:
            chains: 链列表
            max_workers: 最大并发数
        """
        if not chains or len(chains) < 2:
            raise ValueError("并行链至少需要2个链")

        self.chains = chains
        self.max_workers = max_workers

    async def run(self, **kwargs) -> Dict[str, Any]:
        """并行执行所有链

        Args:
            **kwargs: 输入参数

        Returns:
            结果字典（键为链索引或类名）
        """
        import asyncio

        # 创建异步任务
        tasks = []
        for i, chain in enumerate(self.chains):
            task = asyncio.create_task(
                self._run_chain(chain, i, **kwargs),
                name=f"chain-{i}-{chain.__class__.__name__}"
            )
            tasks.append(task)

        # 等待所有任务完成
        results = await asyncio.gather(*tasks)

        # 返回结果字典
        return {
            f"chain_{i}": result
            for i, result in enumerate(results)
        }

    async def _run_chain(self, chain: BaseChain, index: int, **kwargs) -> Any:
        """运行单个链

        Args:
            chain: 要运行的链
            index: 链索引
            **kwargs: 输入参数

        Returns:
            链输出
        """
        try:
            return await chain.run(**kwargs)
        except Exception as e:
            logger.error(f"链 {index} 执行失败: {str(e)}")
            raise

    async def batch(self, inputs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量并行执行

        Args:
            inputs: 输入列表

        Returns:
            输出列表
        """
        results = []
        for input_data in inputs:
            result = await self.run(**input_data)
            results.append(result)
        return results


class ConditionalChain(BaseChain):
    """条件链 - 根据条件选择执行的链"""

    def __init__(
        self,
        condition_func: Callable[[Dict[str, Any]], bool],
        true_chain: BaseChain,
        false_chain: Optional[BaseChain] = None
    ):
        """初始化条件链

        Args:
            condition_func: 条件函数
            true_chain: 条件为真时执行的链
            false_chain: 条件为假时执行的链
        """
        self.condition_func = condition_func
        self.true_chain = true_chain
        self.false_chain = false_chain

    async def run(self, **kwargs) -> Any:
        """根据条件执行链

        Args:
            **kwargs: 输入参数

        Returns:
            选中链的输出
        """
        is_true = self.condition_func(kwargs)

        if is_true:
            logger.info("条件为真，执行 true_chain")
            return await self.true_chain.run(**kwargs)
        elif self.false_chain:
            logger.info("条件为假，执行 false_chain")
            return await self.false_chain.run(**kwargs)
        else:
            logger.info("条件为假，无 false_chain，返回输入")
            return kwargs

    async def batch(self, inputs: List[Dict[str, Any]]) -> List[Any]:
        """批量根据条件执行链

        Args:
            inputs: 输入列表

        Returns:
            输出结果列表
        """
        results = []
        for input_data in inputs:
            result = await self.run(**input_data)
            results.append(result)
        return results


class SimpleChain(BaseChain):
    """简单链 - 单个函数的包装"""

    def __init__(self, func: Callable, name: Optional[str] = None):
        """初始化简单链

        Args:
            func: 要包装的函数
            name: 链名称
        """
        self.func = func
        self.name = name or func.__name__

    async def run(self, **kwargs) -> Any:
        """执行函数

        Args:
            **kwargs: 输入参数

        Returns:
            函数输出
        """
        logger.info(f"执行函数: {self.name}")
        return self.func(**kwargs)

    async def batch(self, inputs: List[Dict[str, Any]]) -> List[Any]:
        """批量执行

        Args:
            inputs: 输入列表

        Returns:
            输出列表
        """
        results = []
        for input_data in inputs:
            result = await self.run(**input_data)
            results.append(result)
        return results


class LLMChain(BaseChain):
    """LLM链 - 用于与LLM交互的链"""

    def __init__(
        self,
        llm: Any,
        prompt: Any,
        output_key: str = "text"
    ):
        """初始化LLM链

        Args:
            llm: LLM对象
            prompt: Prompt对象
            output_key: 输出键名
        """
        self.llm = llm
        self.prompt = prompt
        self.output_key = output_key

    async def run(self, **kwargs) -> str:
        """运行LLM链

        Args:
            **kwargs: 输入参数

        Returns:
            LLM输出
        """
        logger.info("执行 LLM 链")
        # 格式化prompt
        formatted_prompt = self.prompt.format(**kwargs)
        # 调用LLM
        response = await self.llm.ainvoke(formatted_prompt)
        return response.content

    async def batch(self, inputs: List[Dict[str, Any]]) -> List[str]:
        """批量执行

        Args:
            inputs: 输入列表

        Returns:
            输出列表
        """
        results = []
        for input_data in inputs:
            result = await self.run(**input_data)
            results.append(result)
        return results


class RetrievalQAChain(BaseChain):
    """检索问答链 - RAG问答链"""

    def __init__(
        self,
        llm: Any,
        vectorstore: Any,
        question_key: str = "question"
    ):
        """初始化检索问答链

        Args:
            llm: LLM对象
            vectorstore: 向量存储
            question_key: 问题键名
        """
        self.llm = llm
        self.vectorstore = vectorstore
        self.question_key = question_key

    async def run(self, **kwargs) -> Dict[str, Any]:
        """运行检索问答

        Args:
            **kwargs: 输入参数

        Returns:
            包含问题、答案和上下文的字典
        """
        question = kwargs.get(self.question_key)
        if not question:
            raise ValueError(f"缺少问题参数: {self.question_key}")

        logger.info(f"执行检索问答: {question}")

        # 检索相关文档
        docs = self.vectorstore.similarity_search(question, k=4)

        # 准备上下文
        context = "\n".join([doc.page_content for doc in docs])

        # 构建提示
        prompt = f"""基于以下上下文回答问题：

上下文：
{context}

问题：{question}

回答："""

        # 调用LLM
        response = await self.llm.ainvoke(prompt)

        return {
            "question": question,
            "answer": response.content,
            "context": context,
            "source_documents": [doc.dict() for doc in docs]
        }

    async def batch(self, inputs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量执行

        Args:
            inputs: 输入列表

        Returns:
            输出列表
        """
        results = []
        for input_data in inputs:
            result = await self.run(**input_data)
            results.append(result)
        return results


class TransformChain(BaseChain):
    """转换链 - 数据转换"""

    def __init__(
        self,
        input_key: str,
        output_key: str,
        transform_func: Callable[[Any], Any]
    ):
        """初始化转换链

        Args:
            input_key: 输入键名
            output_key: 输出键名
            transform_func: 转换函数
        """
        self.input_key = input_key
        self.output_key = output_key
        self.transform_func = transform_func

    async def run(self, **kwargs) -> Dict[str, Any]:
        """执行转换

        Args:
            **kwargs: 输入参数

        Returns:
            转换后的数据
        """
        input_value = kwargs.get(self.input_key)
        logger.info(f"执行转换: {self.input_key} -> {self.output_key}")

        transformed_value = self.transform_func(input_value)

        return {
            **kwargs,
            self.output_key: transformed_value
        }

    async def batch(self, inputs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量执行

        Args:
            inputs: 输入列表

        Returns:
            输出列表
        """
        results = []
        for input_data in inputs:
            result = await self.run(**input_data)
            results.append(result)
        return results


class StuffDocumentsChain(BaseChain):
    """文档组合链 - 将多个文档组合为一个文档"""

    def __init__(
        self,
        llm: Any,
        input_key: str = "input_documents",
        output_key: str = "output_text",
        document_separator: str = "\n\n"
    ):
        """初始化文档组合链

        Args:
            llm: LLM对象
            input_key: 输入键名
            output_key: 输出键名
            document_separator: 文档分隔符
        """
        self.llm = llm
        self.input_key = input_key
        self.output_key = output_key
        self.document_separator = document_separator

    async def run(self, **kwargs) -> Dict[str, Any]:
        """组合文档

        Args:
            **kwargs: 输入参数

        Returns:
            组合后的文档
        """
        docs = kwargs.get(self.input_key, [])
        if not docs:
            raise ValueError(f"缺少文档参数: {self.input_key}")

        logger.info(f"组合 {len(docs)} 个文档")

        # 组合文档
        combined_doc = self.document_separator.join([str(doc) for doc in docs])

        # 调用LLM处理
        response = await self.llm.ainvoke(combined_doc)

        return {
            **kwargs,
            self.output_key: response.content
        }

    async def batch(self, inputs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量执行

        Args:
            inputs: 输入列表

        Returns:
            输出列表
        """
        results = []
        for input_data in inputs:
            result = await self.run(**input_data)
            results.append(result)
        return results


class ChainManager:
    """链管理器 - 管理多个链"""

    def __init__(self):
        """初始化链管理器"""
        self.chains: Dict[str, BaseChain] = {}

    def register(self, name: str, chain: BaseChain) -> None:
        """注册链

        Args:
            name: 链名称
            chain: 链对象
        """
        self.chains[name] = chain

    def get(self, name: str) -> Optional[BaseChain]:
        """获取链

        Args:
            name: 链名称

        Returns:
            链对象
        """
        return self.chains.get(name)

    def create_pipeline(self, chain_names: List[str]) -> BaseChain:
        """创建管道

        Args:
            chain_names: 链名称列表

        Returns:
            管道链
        """
        chains = [self.chains[name] for name in chain_names if name in self.chains]
        if len(chains) < 2:
            raise ValueError("管道至少需要2个链")

        pipeline = chains[0]
        for chain in chains[1:]:
            pipeline = pipeline | chain

        return pipeline

    def list_chains(self) -> List[str]:
        """列出所有链名称

        Returns:
            链名称列表
        """
        return list(self.chains.keys())


# 全局链管理器实例
chain_manager = ChainManager()


def register_chain(name: str, chain: BaseChain) -> None:
    """便捷函数：注册链"""
    chain_manager.register(name, chain)


def get_chain(name: str) -> Optional[BaseChain]:
    """便捷函数：获取链"""
    return chain_manager.get(name)


def create_chain_pipeline(chain_names: List[str]) -> BaseChain:
    """便捷函数：创建管道"""
    return chain_manager.create_pipeline(chain_names)


# 使用示例
if __name__ == "__main__":
    import asyncio

    async def simple_transform(data: str) -> str:
        """简单转换函数"""
        return data.upper()

    async def simple_process(data: str) -> str:
        """简单处理函数"""
        return f"处理结果: {data}"

    # 创建简单链
    transform_chain = SimpleChain(simple_transform)
    process_chain = SimpleChain(simple_process)

    # 创建顺序链
    sequential = transform_chain | process_chain

    # 运行
    async def main():
        result = await sequential.run(data="hello world")
        print(f"顺序链结果: {result}")

        # 并行链
        parallel = transform_chain & process_chain
        result = await parallel.run(data="test")
        print(f"并行链结果: {result}")

        # 条件链
        def is_long_text(data: dict) -> bool:
            return len(data.get("text", "")) > 10

        long_text_chain = SimpleChain(lambda **k: k.get("text", ""))
        short_text_chain = SimpleChain(lambda **k: "文本较短")

        conditional = ConditionalChain(is_long_text, long_text_chain, short_text_chain)

        result1 = await conditional.run(text="这是一个很长的文本")
        print(f"条件链结果1: {result1}")

        result2 = await conditional.run(text="短文本")
        print(f"条件链结果2: {result2}")

    asyncio.run(main())
