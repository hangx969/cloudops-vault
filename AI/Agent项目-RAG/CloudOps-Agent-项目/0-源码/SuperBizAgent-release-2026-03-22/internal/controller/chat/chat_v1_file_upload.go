package chat

import (
	"SuperBizAgent/api/chat/v1"
	"SuperBizAgent/internal/ai/agent/knowledge_index_pipeline"
	loader2 "SuperBizAgent/internal/ai/loader"
	"SuperBizAgent/utility/client"
	"SuperBizAgent/utility/common"
	"SuperBizAgent/utility/log_call_back"
	"context"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/cloudwego/eino/components/document"
	"github.com/cloudwego/eino/compose"
	"github.com/gogf/gf/v2/errors/gerror"
	"github.com/gogf/gf/v2/frame/g"
	"github.com/gogf/gf/v2/os/gfile"
)

func (c *ControllerV1) FileUpload(ctx context.Context, req *v1.FileUploadReq) (res *v1.FileUploadRes, err error) {
	// 从请求中获取上传的文件
	r := g.RequestFromCtx(ctx)
	uploadFile := r.GetUploadFile("file")
	if uploadFile == nil {
		return nil, gerror.New("请上传文件")
	}

	// 确保保存目录存在
	if !gfile.Exists(common.FileDir) {
		if err := gfile.Mkdir(common.FileDir); err != nil {
			return nil, gerror.Wrapf(err, "创建目录失败: %s", common.FileDir)
		}
	}

	// 获取原始文件名
	newFileName := uploadFile.Filename
	// 完整的保存路径
	savePath := filepath.Join(common.FileDir)

	// 保存文件
	_, err = uploadFile.Save(savePath, false)
	if err != nil {
		return nil, gerror.Wrapf(err, "保存文件失败")
	}

	// 获取文件信息
	fileInfo, err := os.Stat(savePath)
	if err != nil {
		return nil, gerror.Wrapf(err, "获取文件信息失败")
	}

	res = &v1.FileUploadRes{
		FileName: newFileName,
		FilePath: savePath,
		FileSize: fileInfo.Size(),
	}
	err = buildIntoIndex(ctx, common.FileDir+"/"+newFileName)
	if err != nil {
		return nil, gerror.Wrapf(err, "构建知识库失败")
	}
	return res, nil
}

func buildIntoIndex(ctx context.Context, path string) error {
	r, err := knowledge_index_pipeline.BuildKnowledgeIndexing(ctx)
	// 删除biz数据metadata中_source一样的数据
	loader, err := loader2.NewFileLoader(ctx)
	if err != nil {
		return err
	}
	docs, err := loader.Load(ctx, document.Source{URI: path})
	if err != nil {
		return err
	}
	cli, err := client.NewMilvusClient(ctx)
	if err != nil {
		return err
	}
	// 查询所有metadata中_source一样的数据并删除
	expr := fmt.Sprintf(`metadata["_source"] == "%s"`, docs[0].MetaData["_source"])
	queryResult, err := cli.Query(ctx, common.MilvusCollectionName, []string{}, expr, []string{"id"})
	if err != nil {
		return err
	} else if len(queryResult) > 0 {
		// 提取所有需要删除的id
		var idsToDelete []string
		for _, column := range queryResult {
			if column.Name() == "id" {
				for i := 0; i < column.Len(); i++ {
					id, err := column.GetAsString(i)
					if err == nil {
						idsToDelete = append(idsToDelete, id)
					}
				}
			}
		}
		// 删除这些数据
		if len(idsToDelete) > 0 {
			deleteExpr := fmt.Sprintf(`id in ["%s"]`, strings.Join(idsToDelete, `","`))
			err = cli.Delete(ctx, common.MilvusCollectionName, "", deleteExpr)
			if err != nil {
				fmt.Printf("[warn] delete existing data failed: %v\n", err)
			} else {
				fmt.Printf("[info] deleted %d existing records with _source: %s\n", len(idsToDelete), docs[0].MetaData["_source"])
			}
		}
	}
	// 重新构建
	ids, err := r.Invoke(ctx, document.Source{URI: path}, compose.WithCallbacks(log_call_back.LogCallback(nil)))
	if err != nil {
		return fmt.Errorf("invoke index graph failed: %w", err)
	}
	fmt.Printf("[done] indexing file: %s, len of parts: %d\n", path, len(ids))
	return nil
}
